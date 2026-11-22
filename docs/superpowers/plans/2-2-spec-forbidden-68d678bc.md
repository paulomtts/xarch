# 2.2 `forbidden` becomes `uses: {never: <list>}`, with the block `never`

Card `68d678bc`, subtask of `9caa480b`. Release step 3 of the 0.3.0 merged order. Stacked on step 2 (card `31fc54c3`,
`tier` renamed `tests`, branch tip `1fcce88`), whose table of retired names holds one entry:
`RETIRED = (Retired(PART, "tier", "renamed in 0.3.0: write tests"),)` at `xarch/modules/spec/domain/profile_keys.py:154`.

## Sources this spec inherits from

The notes live in `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/`. `KN` is `key-names-design.md`, `R3` is
`0.3.0-cohesion-review-3.md`.

- KN lines 12-16, ruling 1: the names a part may never use sit in a `uses:` group, `uses: {never: pure}`; the top-level
  block is renamed `never:`; this supersedes `may_not_use` everywhere. Lines 41-43, rulings 13-15: the rule id is
  `never-use` (R1), the tier switch is `tiers.<t>.uses: {apply_never: true}` (R2), `review.never` keeps its name (R5).
- KN lines 51-52: a key that names a list keeps a bare name, `uses: {never: pure}`.
- KN 1.1, line 117: `may_not_use` never shipped and gets no retired entry; the old keys go straight to their 0.3.0 form.
  R3 C1, lines 92-100, says the same.
- KN 1.2, lines 123-130: `uses: {never: pure}` points at `never.pure`; the pointer is a bare list name; a part names one
  list; `uses` is a group of the part, outside `imports`.
- KN 1.3, lines 134-150: the table of knock-on names (finding keys, `where` line `never uses:` and JSON field
  `never_uses`, `Loosened` keys `uses.never` and `uses.apply_never`, the `profile explain` entries, the generated docs
  line, the `hints` key, the `alike` text). Lines 165-170: the finding text and fix text stay. Lines 172-178: the
  rules of the `uses` group.
- KN 1.4, lines 182-187: what the rule id rename touches (`RULES`, the README list a test pins, the JSON `rule` field,
  the tag at the end of each message, `hints` keys, the ids a check of the profile's own may not take).
- KN 1.6, lines 218-243 (what changes), 245-254 (what stays), 256-264 (internal identifiers are a later step).
- KN 2, lines 280-286: `never` against `review.never` (each explain text names the other in one clause) and against
  the check language's `may_not` (the explain text of `uses.never` says "the built-in form of a check `may_not` over
  names used"). Line 291: `apply_never` read as "never apply"; the explain text carries it.
- KN 3, lines 303-337: every place that changes, items 1-14 for this step's names.
- KN 4, lines 341-356: the refusals, word for word, and the three misplaced forms; one problem per retired key.
- KN 5 item 3, lines 382-385: the scope of this step and "tests first for the four refusals and the three misplaced
  forms". Lines 370-373: the gates.
- KN "Dodges", lines 405-423.
- R3 C14, lines 207-212 (rule id `never-use`); C15, lines 214-219 (the `never`-under-`imports` hint, see section 3.4).
- R3 section 2: O2 (line 226, each step edits its own tokens of the "use ..." lists, no loosening), O3 (227, key table
  row and `keys.yaml` entry in one commit), O4, O5 (228-229, README and CHANGELOG under `[Unreleased]`), O6 (230, the
  needs walker of step 11 walks step 3's `uses` from then), O8 (232, golden docs regenerated, diff read), O9 (233),
  O10 (234, recorded findings: each step its find and replace, reviewed line by line), O11 (235, `evals.py`), O16
  (240, `where`).
- R3 section 3, line 260: row 3 of the merged order.

## What is there now

At `1fcce88`:

- Key table (`xarch/modules/spec/domain/key_table.py`): `Key(PROFILE, "forbidden", rules=("forbidden",))` (53),
  `Key(PART, "forbidden", rules=("forbidden",))` (80), `Key(TIER, "apply_forbidden", rules=("forbidden",))` (88);
  `NEEDS["parts.<part>.forbidden"]` (200) and `NEEDS["tiers.<tier>.apply_forbidden"]` (204), both `_FORBIDDEN` (186).
  No part or tier key opens a scope except `Key(TIER, "docs", opens=TIER_DOCS)` (95), the precedent for a nested group
  (scope constant and `SCOPES` entry in `profile_keys.py:17, 42`; parsed by `_tier_docs`, `profile_parsing.py:625-643`).
- Parser (`xarch/modules/spec/application/logic/profile_parsing.py`): docstring 25, 31, 35; `_forbidden_lists` (444-457)
  and `_forbidden_refs` (460-477) with their messages; the tier read of `apply_forbidden` (596-599). `forbidden_names`
  (`profile_checks.py:609`) gives the problems of a list's entries at the address it is handed.
- The needs check (`profile_needs._configured`, lines 18-39) reads the keys of a part and of a tier one level deep only.
- Rule id: `RULES` (`xarch/kernel/violations.py:10`) holds `"forbidden"` third. The engine:
  `expansion._forbidden` (49-67, `Rule("forbidden", ...)`, `key=f"parts.{part}.forbidden"` and
  `key=f"parts.{part}.forbidden; tiers.{tier.name}.apply_forbidden"`), `KEYS` (354, `"parts.forbidden"`,
  `"tiers.apply_forbidden"`), the book entry `"forbidden"` (367), `source_check.py:90` (`book["forbidden"]`).
- `looseness.py`: `LOOSER` (34-35), the loosenings (70, 87), the sentences (152-153, 166-167).
- `xarch/cli/reports/where_report.py`: label `may not use` (62, 81), JSON field `forbidden` (114, 120, 134).
- `evals.py`: docstring (6), `_RULED` (61), the `alike` refusal text (150-152).
- `vocabulary.py:347`: the variable `key`'s example `parts.store.forbidden`.
- `docs_template.py`: the prose at 34, `_forbidden_line` (450-463), whose text begins "`forbidden`: a part neither
  imports nor uses by name what is listed for it".
- `keys.yaml` (`xarch/architectures/presets/format/keys.yaml`): entries `forbidden` (154-172), `parts.<part>.forbidden`
  (421-428), `tiers.<tier>.apply_forbidden` (474-481), and the `evals.placement.alike` text (near 1192) that says
  "forbidden, holds and immutable".
- The template `xarch/architectures/testing.md:225` (the enforcement paragraph: "a `forbidden` name dropped", "a tier
  ... no longer `apply_forbidden`"); `xarch/architectures/agents.md:58` ("its `may_import`, `libraries` or `forbidden`
  entries").
- Profiles: `architecture.yaml` (14 part `forbidden:` lines, one top-level block, `apply_forbidden: true` at 267, 279),
  `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml` (each 11 part lines, one block, one or two
  `apply_forbidden`, and prose naming `` `forbidden` `` in litmus texts and `tiers.unit.docs.may_touch`, for instance
  `web.yaml:18, 32, 48, 175, 193, 227`); corpora `tests/bootstrap/corpora/stress.yaml` (14 lines), `7cc6111.yaml` (7),
  `df537ca.yaml` (10).
- Recorded findings: `df537ca.json` holds 21 findings with rule `forbidden`, each message ending
  `(parts.services.forbidden)`; `stress-7cc6111.json.xz` holds 23 (22 ending `(parts.<p>.forbidden)`, one ending
  `(parts.controller.forbidden; tiers.integration.apply_forbidden)`) and 3 findings of other rules whose message or
  fix names archived source (`xarch.modules.rules.application.logic.forbidden`, `forbidden_names`); `7cc6111.json`
  holds no finding of rule `forbidden`, and its 2 mentions are the name `forbidden_names` of archived source. Each
  finding is `[kind, rule, file, line, message, fix]`.
- Golden docs (`tests/bootstrap/test_docs_templates.py:29-31, 58-67`, byte for byte): every `.md` under `docs/cli/`,
  `docs/web/` and `docs/xarch/`. They name the key or the rule id at `docs/cli/testing.md:33, 341, 370`,
  `docs/web/testing.md:33, 342, 371`, `docs/xarch/testing.md:157`, and in the litmus prose of
  `docs/cli/architecture.md` and `docs/web/architecture.md`. "anything not listed is forbidden" in each
  `architecture.md` is English, and `forbidden_imports` in `docs/xarch/architecture.md` is example code.
- README: key summary 117-120, rule table 271 and 296, the JSON example 328-329, the rule id list 358 (pinned to
  `RULES` by `tests/architecture/test_readme.py:29-31`), `Loosened` keys 365-366 and 409-410, `where` 475, 507, 527,
  `alike` near 730, the linter line near 1036.
- CHANGELOG `[Unreleased]`, "Changed": three entries (archived profiles, retired names, `tier` renamed `tests`).

## Required behavior

### 1. The new keys

1. **Top-level `never`.** The block of named lists is `never: {<list>: [<name>, ...]}`. It accepts what `forbidden`
   accepted, entry for entry, and nothing else. Its problems read as today's with `forbidden` replaced by `never`:
   - `never: must be a mapping of list names to lists of dotted names, such as {pure: [datetime.datetime.now, socket]}`
   - `never: '<name>' is not a list name: use letters, digits, '_' and '-'`
   - the entry problems of `forbidden_names`, at the address `never.<list>` (for instance
     `never.pure: must be a non-empty list of dotted names or import names, such as [datetime.datetime.now, socket]`).
2. **A part's `uses` group.** A part writes `uses: {never: <list>}`. `uses` holds exactly one key, `never`, in 0.3.0.
   - `uses` that is no mapping: `parts.<p>.uses: must be a mapping {never}, such as {never: pure}`.
   - `uses: {}`: `parts.<p>.uses: says nothing: write never, or drop it`.
   - An unknown key under it (`only`, `forbidden`, anything): `parts.<p>.uses: unknown key 'only': use never`, through
     the shared unknown-key path with the scope of the group, so the retired-names table is read there too (it holds
     no entry under that scope).
   - `uses.never` a list (of names or of list names): `parts.<p>.uses.never: names one list under never: write the name
     of a list, such as pure`. The note's trailing clause "a list may include others (list-reuse)" is not written in
     this step: list includes do not exist until story 3 (release step 7a), which adds the clause with the feature.
   - `uses.never` any other non-string (number, boolean, mapping, null): `parts.<p>.uses.never: must be the name of a
     list under `never``.
   - `uses.never` naming no list: `parts.<p>.uses.never: no list named 'x': use pure, published, or write it under
     `never`` (the lists sorted), or `... no list named 'x': write it under `never`` when the file has no `never`.
   - When the top-level `never` is itself refused (no mapping), the parts' `uses.never` give no problem of their own, as
     today.
   - A part with `uses: {never: pure}` loads into the same `Architecture` a part with `forbidden: pure` loaded into: the
     same names held, the same findings, the same docs but for the words of sections 2 and 5.
3. **A tier's `uses` group.** A tier writes `uses: {apply_never: true}`. `uses` holds exactly one key, `apply_never`.
   - `uses` that is no mapping: `tiers.<t>.uses: must be a mapping {apply_never}, such as {apply_never: true}`.
   - `uses: {}`: `tiers.<t>.uses: says nothing: write apply_never, or drop it`.
   - An unknown key under it (`never`, anything): `tiers.<t>.uses: unknown key 'never': use apply_never`.
   - `apply_never` not a boolean: `tiers.<t>.uses.apply_never: must be true or false: whether its tests are held to the
     `uses.never` list of the part they mirror`.
   - `uses: {apply_never: false}` is accepted and is the same as no `uses`. `apply_never: true` holds the tier's tests
     to the list of each part they mirror, as `apply_forbidden: true` did.
4. **Key table and needs.** The table holds `Key(PROFILE, "never", rules=("never-use",))`, `Key(PART, "uses",
   opens=PART_USES)` with `Key(PART_USES, "never", rules=("never-use",))`, and `Key(TIER, "uses", opens=TIER_USES)`
   with `Key(TIER_USES, "apply_never", rules=("never-use",))`; scopes `PART_USES` at `parts.<part>.uses` and
   `TIER_USES` at `tiers.<tier>.uses`. `NEEDS` moves to `parts.<part>.uses.never` and `tiers.<tier>.uses.apply_never`
   with the same facts. No row `forbidden` or `apply_forbidden` remains in any scope, and no row `never` sits under
   `PART` or `apply_never` under `TIER`.
   - The needs check sees the keys of a part's and a tier's `uses` group: a profile whose language does not supply a
     fact `uses.never` reads is refused with `parts.<p>.uses.never: its check reads <fact> (...), which the language
     <l> does not supply: drop parts.<p>.uses.never, or check the app with a language whose reader supplies <fact>`, and
     the same for `tiers.<t>.uses.apply_never`; `apply_never: false` needs nothing. This is the behavior `forbidden`
     and `apply_forbidden` have today, kept. How the walker reaches the group is the planner's (one level into the
     scope a set part or tier key opens is enough; R3 O6 leaves the general walker to step 11).
5. **Rule id `never-use`.** `RULES` holds `"never-use"` in the place `"forbidden"` held; `"rules"` stays (step 2.3).
   - Every finding of the check has rule `never-use`, in text output, in `--format json`'s `rule`, and as the tag at
     the end of its message line wherever the rule id is printed.
   - The finding message keeps its words and ends with the new key: `domain/ of modules/docs may not import socket
     (parts.domain.uses.never)`; a test's: `... (parts.domain.uses.never; tiers.unit.uses.apply_never)`. The fix text
     is unchanged.
   - `hints: {never-use: <text>}` is accepted; a check of the profile's own may not take the id `never-use` and may
     take the id `forbidden`.
   - `xarch profile explain parts.uses.never --rule` (and `tiers.uses.apply_never --rule`) shows the rules the key
     expands to, as `parts.forbidden --rule` did; `KEYS` names `parts.uses.never` and `tiers.uses.apply_never`.
6. **`profile explain` texts.** Entries `never`, `parts.<part>.uses`, `parts.<part>.uses.never`, `tiers.<tier>.uses`,
   `tiers.<tier>.uses.apply_never` exist in `keys.yaml`, each with an example that loads; the entries `forbidden`,
   `parts.<part>.forbidden`, `tiers.<tier>.apply_forbidden` are gone. Wording is the planner's, within these limits:
   - `never`: the meaning of today's `forbidden` entry, a part pointing at a list with `uses: {never: <list>}`, and one
     clause naming `review.never` as a different list (files review never sends).
   - `parts.<part>.uses`: the group of what the part's code uses; holds `never`.
   - `parts.<part>.uses.never`: the list of names the part never uses; accepts the name of one list under the top-level
     `never`; says it is the built-in form of a check `may_not` over names used. It bans names of code, never says it
     bans imports of parts (dodge, KN line 420).
   - `tiers.<tier>.uses`: holds `apply_never`.
   - `tiers.<tier>.uses.apply_never`: true or false, a switch and not a list: whether the tier's tests are held to the
     `uses.never` list of the part they mirror.
   - `review.never`'s text gains one clause naming the top-level `never` as the other list (KN line 282), if it names
     none today.
   - No text of `keys.yaml` names `forbidden` or `apply_forbidden` as a key of the format; the `evals.placement.alike`
     text names `uses.never` where it named `forbidden`.

### 2. Other outputs that name the key

1. **`where`.** The text line reads `never uses: <names>` where it read `may not use: <names>`, at both places the
   report prints it. The JSON field is `never_uses` where it was `forbidden`, with the same value, in every shape of
   the report that held it (empty-answer default included). Every other field and label is unchanged. The Python field
   of the contract (`rules/contract/__init__.py:188, 227`) may keep its name in this step: the report maps it to JSON by
   hand; its rename is step 2.4.
2. **`Loosened`.** The keys are `uses.never` and `uses.apply_never` where they were `forbidden` and `apply_forbidden`,
   in `LOOSER`, in the JSON the enforcement section reports, and as printed labels. The sentences read:
   - `<part> no longer forbids <what> (parts.<part>.uses.never)`
   - `the <tier> tests are no longer held to their part's never list (tiers.<tier>.uses.apply_never)`

   `review.never` stays a key of its own, unchanged.
3. **`evals.placement.alike`.** `_RULED` names `uses.never` where it named `forbidden`, so a group of parts differing
   in their list is refused with `... differ in uses.never: ... write the same uses.never, holds and immutable for each,
   or drop the group` (and "differ in uses.never and holds" etc. as the `_and` join gives). The final wording of
   code-shape (step 12) is not written here.
4. **Check language.** The variable `key`'s example reads `parts.store.uses.never, checks.<id>`.
5. **Agent prose.** `xarch/architectures/agents.md:58` reads "its `may_import`, `libraries` or `uses.never` entries".

### 3. The old names are refused

1. `RETIRED` holds exactly these entries, the step-2 one kept first, the rest in this order:
   - `Retired(PART, "tier", "renamed in 0.3.0: write tests")`
   - `Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}")`
   - `Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}")`
   - `Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never")`
   - `Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use")`
   - `Retired(PART, "never", "a key of uses: write uses: {never: <list>}")`
   - `Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}")`

   No entry for `may_not_use` or any spelling of it. No code tests for any of these names (no `if key == "forbidden"`):
   each refusal comes from the table through the readers step 1 built.
2. The refusals, word for word (the "use" list is the keys of the day, sorted, as section 6 lists them):
   - `parts.<p>: unknown key 'forbidden': moved in 0.3.0: write uses: {never: <list>}; use <part keys>`
   - `tiers.<t>: unknown key 'apply_forbidden': moved in 0.3.0: write uses: {apply_never: true}; use <tier keys>`
   - `unknown key 'forbidden': renamed in 0.3.0: write never; use <file keys>`
   - `hints.forbidden: unknown rule id 'forbidden': renamed in 0.3.0: write never-use; use <rule ids and own ids>`
   - `parts.<p>: unknown key 'never': a key of uses: write uses: {never: <list>}; use <part keys>`
   - `tiers.<t>: unknown key 'apply_never': a key of uses: write uses: {apply_never: true}; use <tier keys>`
3. The value written under a retired name is never shown. Exit codes are those of a profile that does not load.
4. One problem per retired name, the retired ones in sorted order, ahead of the joined message of the keys only
   unknown, which is unchanged. A part of an old profile writing `forbidden` and `tier` gets two problems,
   `unknown key 'forbidden': ...` then `unknown key 'tier': ...`.
5. A file writing the old top-level `forbidden` and parts writing `forbidden: pure` gets the file's problem and one per
   part; it does not also get problems for the parts' references, since nothing reads them.
6. A file writing `forbidden` and `never` both gets the retired problem for `forbidden`, and its `never` is read as
   written (so a valid `never` adds no problem, an invalid one adds its own). A part writing `forbidden` and `uses`
   both gets the retired problem for `forbidden`, and its `uses` is read as written in the same way.
7. `hints.forbidden` beside a check of the profile's own whose id is `forbidden` is accepted: it is a hint for that
   check (the id is no longer taken).
8. `xarch profile explain` answers each retired address with the entry's text, exit 2, `retired: "<text>"` in its JSON,
   as step 1 built: `forbidden` ("renamed in 0.3.0: write never"), `parts.forbidden` and `parts.<part>.forbidden`
   ("moved in 0.3.0: write uses: {never: <list>}"), `tiers.apply_forbidden` and `tiers.<tier>.apply_forbidden`,
   `parts.never`, `tiers.apply_never`. `profile explain never`, `parts.uses.never`, `tiers.uses.apply_never` and
   `review.never` explain their keys, exit 0.
9. **The fourth misplaced form is not built here.** KN 4 (line 352-353) and R3 C15 name a third misplaced form,
   `never` under a part's `imports` ("a key of uses, beside imports: write uses: {never: <list>}"). No `imports` scope
   exists at this step: the group is built in release step 13 (code-shape 5), and an entry under a scope with no
   address would be dead (`key_lookup._at` requires the scope in `SCOPES`; `test_profile_keys.py:8-11` refuses it).
   That entry and its test belong to step 13, which creates the scope. This spec records the deferral; the planner adds
   no placeholder for it.

### 4. The profiles and corpora

1. Every `forbidden: <list>` line of a part in `architecture.yaml`, `xarch/architectures/cli.yaml`,
   `xarch/architectures/web.yaml`, `tests/bootstrap/corpora/stress.yaml`, `7cc6111.yaml` and `df537ca.yaml` reads
   `uses: {never: <list>}` (or the block form, the file's style either way), the top-level block reads `never:`, and
   every `apply_forbidden: true` reads `uses: {apply_never: true}`. The lists' entries and order are unchanged.
2. Prose in those files that names the key in backticks names `uses.never` ("holds it to its `uses.never` list",
   "checked by `uses.never`"). English "forbidden" in prose that is not the key stays.
3. After the edit, `grep -nw 'forbidden\|apply_forbidden'` in the three bundled profiles and the three corpus profiles
   returns nothing.
4. The `.tar.xz` archives are not touched. The recorded findings change only as follows, by hand, each line read:
   - `df537ca.json`: the 21 findings of rule `forbidden` get rule `never-use` and their message's
     `(parts.services.forbidden)` becomes `(parts.services.uses.never)`.
   - `stress-7cc6111.json.xz`: unpacked, the 23 findings of rule `forbidden` get rule `never-use`, `(parts.<p>.forbidden)`
     becomes `(parts.<p>.uses.never)`, and `(parts.controller.forbidden; tiers.integration.apply_forbidden)` becomes
     `(parts.controller.uses.never; tiers.integration.uses.apply_never)`; repacked as xz. The 3 findings naming
     `xarch.modules.rules.application.logic.forbidden` and `forbidden_names`, and every `file` field naming an archived
     file such as `test_forbidden.py`, stay.
   - `7cc6111.json`, `examples-cli.json`, `examples-web.json`: unchanged.
   - Nothing is recorded by running the code under test. The diff of the unpacked recordings shows only the lines
     above.
5. `test_recorded_corpora.py` passes against the edited recordings.
6. `xarch profile check architecture.yaml`, `xarch check` and `xarch check --strict` pass on this repository.

### 5. Generated docs

1. The rule line of the generated testing doc reads "`never-use`: a part neither imports nor uses by name what its
   `uses.never` list names (<parts>: <names>)<tests>. ..." (KN line 148); the rest of the line is unchanged. The
   template's prose at `docs_template.py:34` names `uses.never` where it named `forbidden`.
2. The enforcement paragraph template (`xarch/architectures/testing.md:225`) names "a `uses.never` name dropped" and "a
   tier no longer `uses.apply_never`".
3. The golden copies are regenerated from the edited profiles and templates (`build_controllers().spec.docs(<profile>)`
   for `cli`, `web` and `architecture.yaml`, written over `docs/cli/`, `docs/web/`, `docs/xarch/`), never edited by
   hand, and the diff is read. The expected moves: `docs/cli/testing.md` and `docs/web/testing.md` lines 33 (tier docs
   prose), 341/342 (rule line), 370/371 (enforcement paragraph); `docs/xarch/testing.md:157`; the litmus prose lines of
   `docs/cli/architecture.md` and `docs/web/architecture.md`. `docs/xarch/architecture.md` is expected not to move:
   `architecture.yaml`'s prose names no key in backticks, and its `forbidden_imports` lines are code of `docs/examples/`.
   Any other moved line is reported as a bug of this step, not hand-edited. "anything not listed is forbidden" stays.

### 6. The "use ..." lists of the day

The unknown-key messages list, sorted:

- part keys: `built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks,
  package_only, path, role, shared, tests, types_only, untested, uses`
- tier keys: `docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses`
- file keys: `based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never,
  parts, reserved, review, testing, tiers`
- rule ids: `RULES` sorted, `never-use` in place of `forbidden`.

### 7. README and CHANGELOG

1. README: the key summary names `uses: {never}` on a part, `never: {<list>: [...]}` at the top, and `uses:
   {apply_never}` on a tier; the rule table row reads `never-use` with keys `never`, `parts.uses.never`,
   `tiers.uses.apply_never`; the JSON example's rule and message use `never-use` and `(parts.domain.uses.never)`; the
   rule id list names `never-use` in `RULES`' order; the `Loosened` key list and prose name `uses.never` and
   `uses.apply_never`; `where` names the line `never uses` and the field `never_uses`; the `alike` and linter lines
   name `uses.never`. The rule id `rules` and every other name stay.
2. CHANGELOG, under `[Unreleased]`, "Changed", one entry after the `tests` one: the part key `forbidden` is now
   `uses: {never: <list>}`, the top-level block `forbidden` is `never`, a tier's `apply_forbidden: true` is
   `uses: {apply_never: true}`, the rule id is `never-use` (in findings, JSON and `hints`), `where` prints `never uses:`
   and its JSON field is `never_uses`, the `Loosened` keys are `uses.never` and `uses.apply_never`; each old name is
   refused with its new form, which `xarch profile explain <old address>` also gives, and `never:` on a part or
   `apply_never:` on a tier is told it is a key of `uses`. Finding and fix texts are otherwise unchanged.

## Error paths, together

| Input | Problems (in order) |
|---|---|
| part `forbidden: pure` | `parts.<p>: unknown key 'forbidden': moved in 0.3.0: write uses: {never: <list>}; use ...` |
| part `forbidden: pure`, `tier: unit` | the `forbidden` one, then the `tier` one (and the `tests` coverage problem as step 2 says) |
| part `never: pure` | `parts.<p>: unknown key 'never': a key of uses: write uses: {never: <list>}; use ...` |
| part `uses: pure` | `parts.<p>.uses: must be a mapping {never}, such as {never: pure}` |
| part `uses: {}` | `parts.<p>.uses: says nothing: write never, or drop it` |
| part `uses: {only: [x]}` | `parts.<p>.uses: unknown key 'only': use never` |
| part `uses: {never: [pure, ambient]}` | `parts.<p>.uses.never: names one list under never: write the name of a list, such as pure` |
| part `uses: {never: 3}` | `parts.<p>.uses.never: must be the name of a list under `never`` |
| part `uses: {never: nope}` | `parts.<p>.uses.never: no list named 'nope': use ambient, pure, or write it under `never`` |
| tier `apply_forbidden: true` | `tiers.<t>: unknown key 'apply_forbidden': moved in 0.3.0: write uses: {apply_never: true}; use ...` |
| tier `apply_never: true` | `tiers.<t>: unknown key 'apply_never': a key of uses: write uses: {apply_never: true}; use ...` |
| tier `uses: {}` | `tiers.<t>.uses: says nothing: write apply_never, or drop it` |
| tier `uses: {never: true}` | `tiers.<t>.uses: unknown key 'never': use apply_never` |
| tier `uses: {apply_never: yes-please}` | `tiers.<t>.uses.apply_never: must be true or false: whether its tests are held to the `uses.never` list of the part they mirror` |
| top-level `forbidden: {...}` | `unknown key 'forbidden': renamed in 0.3.0: write never; use ...` |
| top-level `never: [x]` | `never: must be a mapping of list names to lists of dotted names, such as {pure: [datetime.datetime.now, socket]}` |
| `hints: {forbidden: see}` | `hints.forbidden: unknown rule id 'forbidden': renamed in 0.3.0: write never-use; use ...` |

Every problem is prefixed with the profile file's name as the loader says it.

## Tests that prove it

Tiers follow `docs/xarch/testing.md`: `tests/modules/spec/domain/` and `tests/modules/spec/application/logic/` are
unit (pure values and parsing of a document, no files), `tests/modules/rules/application/logic/` unit for the engine's
pure expansion, `tests/cli/` the report renderers, `tests/bootstrap/` the tier that loads real profile files and runs
the CLI and the recorded corpora; `tests/architecture/` the repo's own guards.

Written first, failing on the parent branch:

1. Unit, `tests/modules/spec/domain/test_profile_keys.py`: the shipped table is exactly the seven entries of 3.1 (in
   place of `test_the_one_name_retired_is_the_part_key_tier_renamed_tests`); the generic assertions stay and pass
   (scope known, one line, no name its scope still has, which proves `never` under `PART` and `apply_never` under
   `TIER` are not keys there, and `forbidden` is no rule id).
2. Unit, `tests/modules/spec/application/logic/test_retired_keys.py`: the shipped table answers `retired` and
   `retired_at` for each entry and each address of 3.8 (`forbidden`, `parts.forbidden`, `parts.<part>.forbidden`,
   `tiers.apply_forbidden`, `tiers.<tier>.apply_forbidden`, `parts.never`, `tiers.apply_never`), and gives "" for
   `parts.uses.never`, `tiers.uses.apply_never`, `never`, `review.never`, `retired(PART_USES, "never")`, and
   `retired(TIER, "forbidden")`. `PART_USE`, `TIER_USE`, `PROFILE_USE` and `RULES_USE` follow section 6.
3. Unit, the four refusals and the two misplaced forms built here, through the parser (`problems(document)` of
   `tests/modules/spec/profiles.py`), each asserting the whole problem list: part `forbidden`; tier `apply_forbidden`;
   top-level `forbidden`; `hints.forbidden`; part `never`; tier `apply_never`. Plus: the value written
   (`forbidden: secret-list`) appears in no problem; a part writing `forbidden` and `tier` gets both in sorted order; a
   file writing `forbidden` and `never` is refused for `forbidden` alone; `hints.forbidden` with an own check named
   `forbidden` loads. These sit with the parser's tests of the keys they move (a new
   `tests/modules/spec/application/logic/test_uses_group.py`, or the existing `test_profile_parsing.py` /
   `test_forbidden.py`; the planner picks one home, unit either way).
4. Unit, the `uses` groups: every row of the error table from `parts.<p>.uses` down to the tier rows, one test per
   message, each the whole problem list; `uses: {never: pure}` loads into the `Architecture` that `forbidden: pure`
   gave (same `forbidden` field value); `uses: {apply_never: false}` and no `uses` give the same tier. Table tests in
   the unit tier hold no branch in their body (`plain_tables`): a parametrised case takes its expected problem as a
   parameter (commit `2228067`).
5. Unit, `tests/modules/spec/application/logic/test_profile_needs.py`: `uses: {never: pure}` on a part with the toy
   language (which supplies no `use`) is refused naming `parts.service.uses.never`; `uses: {apply_never: true}` on a
   tier the same for `tiers.unit.uses.apply_never`; `apply_never: false` configures nothing; the "found in every
   scope" test lists the two new addresses where it sets them.
6. Unit, `tests/modules/rules/application/logic/` (`test_forbidden.py`, `test_expansion.py`, `test_explained.py`):
   the rule's id is `never-use` and its keys `parts.<p>.uses.never` and `parts.<p>.uses.never; tiers.<t>.uses.apply_never`;
   `keyed(rules, "tiers.uses.apply_never")` finds the test rule; `KEYS` holds the new addresses.
7. Unit, `tests/kernel/test_violations.py` and the rule-id tests (`test_rule_ids.py`): `never-use` is a rule id,
   `forbidden` is not; a check of the profile's own named `never-use` is refused and one named `forbidden` loads.
8. Unit, `test_looseness.py`: the two sentences of 2.2 and keys `uses.never`, `uses.apply_never`.
9. Unit, `test_evals.py`: the `alike` refusal names `uses.never`.
10. Unit, `test_where.py` (rules logic) and the `where` report test under `tests/cli/`: the text line `never uses:` and
    the JSON field `never_uses`, no field `forbidden`.
11. Unit, `test_docs_template.py`: the rule line begins "`never-use`: a part neither imports nor uses by name what its
    `uses.never` list names".
12. Unit, `tests/modules/spec/application/test_explain.py`: `Shown` cases for the five new entries, the old addresses
    retired with their texts.
13. Bootstrap, `tests/bootstrap/test_profile_explain.py`: `profile explain parts.forbidden` exits 2 with "moved in
    0.3.0: write uses: {never: <list>}" and `retired` in JSON; `profile explain forbidden` exits 2 with "renamed in
    0.3.0: write never"; `parts.never` exits 2; `never`, `parts.uses.never`, `tiers.uses.apply_never`, `review.never`
    exit 0.
14. Bootstrap, a real profile file on disk (`test_profile_file.py` or `test_architecture_files.py`): a part writing
    `forbidden:` does not load, with the refusal in the output word for word.

Edited in place (fixtures and assertions; none loosened to `"unknown key" in output`):

15. Every fixture and builder writing `forbidden`/`apply_forbidden` (`tests/modules/spec/profiles.py`,
    `tests/modules/rules/builders.py`, `tests/modules/spec/application/origins.py`, `test_needs_agree.py`'s
    `EVERY_KEY`, and the files the explore step listed) writes the new form; every hard-coded "use ..." list swaps its
    own tokens per section 6 (`test_profile_parsing.py:164`'s part-key list, `test_profile_parsing_tests.py`'s lists
    near 172 and 347); every assertion of the rule id `forbidden` reads `never-use`.
16. `test_key_catalogue.py` and `test_needs_agree.py` pass with the key table and `keys.yaml` changed in one commit.
17. Bootstrap: the bundled-profile tests load the edited profiles; `test_recorded_corpora.py` passes against the
    hand-edited recordings; `test_docs_templates.py` passes against the regenerated golden docs;
    `tests/architecture/test_readme.py` passes against the README's rule list.

## Out of scope

- The rule id `rules` and its retired entry (card 2.3, release step 4): `RULES` keeps `"rules"`, recorded `rules`
  findings keep their rule field.
- Internal identifiers (card 2.4, release step 5): `Architecture.forbidden`, `Part/Tier/Profile/CheckedTier/InPart
  .forbidden`, `_forbidden_lists`, `_forbidden_refs`, `forbidden_names`, `FORBIDDEN_FIX`, `_forbidden_line`,
  `_FORBIDDEN`, `expansion._forbidden`, the contract field behind `where`'s `never_uses`, test file names such as
  `test_forbidden.py`. Only profile-facing words move here, plus the strings that are output or lookups (`key=`
  strings, `KEYS`, the book entry name, the rule id).
- List includes (`never: {published: [pure, typing.Any]}`) and the "a list may include others" clause (story 3,
  release step 7a).
- The `imports` group and the misplaced form `never` under `imports` (release step 13; see 3.9).
- The general needs walker (release step 11).
- `uses.only` (dodge: not built in 0.3.0).
- The final `alike` wording of code-shape (release step 12).
- `review.never`, `guards.scenario-coverage.tier`, `in.tier`: unchanged.
- `docs/examples/` (placement examples read by `review calibrate`), `xarch/architectures/examples`, the `.tar.xz`
  archives, the 0.2.0 CHANGELOG entry, `docs/superpowers/` history notes, English "forbidden" in prose.
- Ordering the CHANGELOG under a 0.3.0 lead and reading the README block whole (release step 25).

## Gates

On this branch alone, each passing: `uv run pytest -q` (in the background, over two minutes, read at the end),
`uv run xarch check`, `uv run xarch check --strict`, `uv run ruff check` (never `--fix`),
`uv run xarch profile check architecture.yaml`.

## Project rules for the planner

No comments in xarch's code (docstrings are fine); tests written first; examples simple, with absolute `app.` imports;
recorded corpora edited by hand only, as section 4.4 says; Python only in the reader adapter and the data files under
`xarch/architectures/presets/`; the key table rows and the `keys.yaml` entries in one commit; golden docs regenerated,
never hand-edited, diff read; README and CHANGELOG lines under `[Unreleased]`; `.claude/` stays out of commits;
nothing is pushed.

## Review focus (for the planner)

1. A blind replace of `forbidden`: it would rewrite archived file names in the recordings (`forbidden_names`,
   `logic.forbidden`, `test_forbidden.py`), English prose ("anything not listed is forbidden"), the 0.2.0 CHANGELOG,
   `docs/examples/`, or internal identifiers that belong to 2.4.
2. `never:` accepted on a part, or `apply_never:` on a tier, outside `uses` (dodge, KN line 410); or `never` accepted
   under a tier's `uses` as a switch.
3. A profile in a language lacking `use`/`method_call` loading with `uses.never` set, because the needs check does not
   look inside the group.
4. The `where` JSON keeping `forbidden` beside `never_uses`, or the label left as `may not use`; `Loosened` keys left
   on the old words in JSON while the sentences change.
5. `uses.never`'s explain text widened to say it bans imports of parts, or a refusal hint echoing the value written.

---

# 2.2 `forbidden` becomes `uses: {never: <list>}`, with the block `never` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A part writes `uses: {never: <list>}` pointing at a list of the top-level block `never:`, a tier writes
`uses: {apply_never: true}`, the check's rule id is `never-use`, every output that named the old keys names the new
ones, and every old or misplaced name is refused through the table of retired names.

**Architecture:** Two new scopes, `PART_USES` (`parts.<part>.uses`) and `TIER_USES` (`tiers.<tier>.uses`), each
opened by a key `uses`, after the precedent of `TIER_DOCS`; one parser helper `_group` reads either group (shape,
"says nothing", unknown keys through the shared path with the group's scope), and `_forbidden_refs`/`_tier` read the
key inside it. The needs walker goes one level into the scope a set part or tier key opens. The engine's key strings,
`KEYS`, the book entry and the rule id move to `never-use`; the `where`, `Loosened` and `alike` outputs and the
generated docs name the new keys; the table of retired names gains six entries that the readers step 1 built turn into
refusals and `profile explain` answers. Internal identifiers (`Architecture.forbidden`, `_forbidden_refs`, ...) keep
their names: that is step 2.4.

**Tech Stack:** Python 3.13, pytest, typer (CLI), PyYAML; run everything through `uv run`.

**Spec:** `docs/superpowers/specs/2-2-spec-forbidden-68d678bc.md` (copied above this line).

## Global Constraints

- `RETIRED` holds exactly, in this order: `Retired(PART, "tier", "renamed in 0.3.0: write tests")`,
  `Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}")`,
  `Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}")`,
  `Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never")`,
  `Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use")`,
  `Retired(PART, "never", "a key of uses: write uses: {never: <list>}")`,
  `Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}")`. No entry for `may_not_use`.
- No code tests for an old name (no `if key == "forbidden"`, no alias): each refusal comes from the table.
- The messages of the new keys, word for word (`<p>` a part, `<t>` a tier):
  - `never: must be a mapping of list names to lists of dotted names, such as {pure: [datetime.datetime.now, socket]}`
  - `never: '<name>' is not a list name: use letters, digits, '_' and '-'`; entry problems at `never.<list>`
  - `parts.<p>.uses: must be a mapping {never}, such as {never: pure}`
  - `parts.<p>.uses: says nothing: write never, or drop it`
  - `parts.<p>.uses: unknown key '<k>': use never`
  - `parts.<p>.uses.never: names one list under never: write the name of a list, such as pure`
  - ``parts.<p>.uses.never: must be the name of a list under `never` ``
  - ``parts.<p>.uses.never: no list named '<x>': use <lists sorted>, or write it under `never` `` (or
    ``... no list named '<x>': write it under `never` `` when `never` holds no list)
  - `tiers.<t>.uses: must be a mapping {apply_never}, such as {apply_never: true}`
  - `tiers.<t>.uses: says nothing: write apply_never, or drop it`
  - `tiers.<t>.uses: unknown key '<k>': use apply_never`
  - ``tiers.<t>.uses.apply_never: must be true or false: whether its tests are held to the `uses.never` list of the part they mirror``
- The "use ..." lists of the day (sorted):
  - part keys: `built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, package_only, path, role, shared, tests, types_only, untested, uses`
  - tier keys: `docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses`
  - file keys: `based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, parts, reserved, review, testing, tiers`
  - rule ids: `RULES` sorted, `never-use` in place of `forbidden`.
- Finding messages end `(parts.<p>.uses.never)` and, for a test, `(parts.<p>.uses.never; tiers.<t>.uses.apply_never)`;
  fix texts are unchanged.
- `Loosened` sentences: `<part> no longer forbids <what> (parts.<part>.uses.never)` and
  `the <tier> tests are no longer held to their part's never list (tiers.<tier>.uses.apply_never)`.
- Stays as it is (step 2.3, 2.4, later steps): the rule id `rules`; `Architecture.forbidden`,
  `Part/Tier/Profile/CheckedTier/InPart/InTests.forbidden`, `_forbidden_lists`, `_forbidden_refs`, `forbidden_names`,
  `FORBIDDEN_FIX`, `_forbidden_line`, `_FORBIDDEN`, `expansion._forbidden`, test file names such as
  `test_forbidden.py`, the test helper `checks.forbidden`; `review.never`; `guards.scenario-coverage.tier`; `in.tier`;
  `docs/examples/`; the `.tar.xz` archives; the 0.2.0 CHANGELOG entry; English "forbidden" in prose ("anything not
  listed is forbidden").
- No comments in xarch's code (docstrings are fine). Tests first (RED before GREEN). `ruff check` is never run with
  `--fix`.
- Unit-tier table tests hold no branch in their body (no `if`, `match`, `try`, `for`, `while`, no `x if y else z`): a
  parametrised case takes its expected problem as a parameter.
- Recorded findings are edited by text only (the script of Task 2), never by running the code under test; the diff is
  read line by line.
- The key table rows and the `keys.yaml` entries change in one commit (Task 1).
- Golden docs (`docs/cli/`, `docs/web/`, `docs/xarch/`) are regenerated by the script of Task 5, never hand-edited; the
  diff is read and any line outside the expected ones is reported, not edited.
- README and CHANGELOG lines go under `[Unreleased]`; `.claude/` and `docs/superpowers/` are never added by the
  engineer's commits; nothing is pushed.
- Never `pkill`/`killall`/`kill` by pattern; wrap long runs in `timeout` or stop them by the PID you recorded.
- Every commit message ends with the attribution line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  (if your harness gives you a different attribution line, use that one instead).

## Review Focus

1. A part writing `uses: {never: false}` (or `null`, a mapping): it must be refused with "must be the name of a list
   under `never`", not pass silently because the needs walker skips `false`. Test: Task 1,
   `test_a_part_s_uses_written_wrong_is_refused_at_its_address`, cases `false`, `null`, `a mapping`.
2. A `uses` written as a YAML list (`uses: [never: pure]` reads as `[{never: pure}]`) or a string: one shape problem,
   and neither the parser nor the needs walker crashes on the non-mapping. Test: Task 1, the cases `a uses written as
   a list` and `a uses that is no mapping`, and `test_a_uses_that_is_no_mapping_configures_nothing_in_any_language`
   in `test_profile_needs.py`.
3. A part naming a list when the file has no `never`, or an empty `never: {}`: told to write it under `never`, never a
   crash and never "use , or write it". Test: Task 1,
   `test_a_part_naming_a_list_the_file_does_not_hold_is_told_to_write_it_under_never`.
4. `never` written under a tier's `uses`, or `apply_never` under a part's `uses`: only unknown under the group, with
   `use apply_never` / `use never`, never accepted as a switch or a list. Test: Task 1, `never under a tier's uses`;
   Task 3, `test_apply_never_under_a_part_s_uses_is_only_unknown_there`.
5. A recorded finding renamed `never-use` that would sort after another rule at the same file and line (the findings
   are sorted by file, line, rule): checked when planning (the only neighbour is `built-by`, which sorts first either
   way), and re-checked by Task 2 Step 7's script output and `test_recorded_corpora.py`.

---

## File map

- `xarch/modules/spec/domain/profile_keys.py` — scopes `PART_USES`, `TIER_USES`; `RETIRED` (Task 3).
- `xarch/modules/spec/domain/key_table.py` — rows `never`, `uses` (part, tier), `uses.never`, `uses.apply_never`;
  `NEEDS`; rule id (Task 2).
- `xarch/architectures/presets/format/keys.yaml` — entries `never`, `parts.<part>.uses`, `parts.<part>.uses.never`,
  `tiers.<tier>.uses`, `tiers.<tier>.uses.apply_never`, `review.never` (Task 1); `evals.placement.alike` (Task 4).
- `xarch/modules/spec/application/logic/profile_parsing.py` — docstring, `_group`, `_forbidden_lists`,
  `_forbidden_refs`, `_tier`.
- `xarch/modules/spec/application/logic/profile_needs.py` — `_configured`, `_grouped`.
- `xarch/modules/spec/application/logic/profile_checks.py`, `xarch/modules/spec/domain/values.py` — docstrings.
- `xarch/kernel/violations.py`, `xarch/modules/rules/application/logic/expansion.py`,
  `xarch/modules/rules/application/services/source_check.py` — rule id, key strings, `KEYS`, book (Task 2).
- `xarch/cli/reports/where_report.py`, `xarch/modules/spec/application/logic/looseness.py`,
  `xarch/modules/spec/domain/published.py`, `xarch/modules/spec/application/logic/evals.py`,
  `xarch/modules/rules/domain/vocabulary.py`, `xarch/architectures/agents.md` (Task 4).
- `xarch/modules/spec/application/logic/docs_template.py`, `xarch/architectures/testing.md`, prose of
  `xarch/architectures/cli.yaml` and `web.yaml`, golden docs (Task 5).
- Profiles/corpora: `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`,
  `tests/bootstrap/corpora/stress.yaml`, `7cc6111.yaml`, `df537ca.yaml` (Task 1 key lines, Task 5 prose).
- Recordings: `tests/bootstrap/corpora/df537ca.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz` (Task 2).
- `README.md` (Task 2 the rule id list, Task 6 the rest), `CHANGELOG.md` (Task 6).

Throwaway files live in `/tmp/xarch-2-2/` and are never committed.

---

### Task 1: The keys `never`, `uses: {never}` and `uses: {apply_never}`

Everything that writes or reads the keys changes together: the scopes, the key table rows and their `keys.yaml`
entries, the parser, the needs walker, the six profile files' key lines and every test fixture. A partial state does
not load the bundled profiles, so this is one task. The rule id stays `forbidden` here (Task 2 renames it), so the new
rows feed `rules=("forbidden",)` for now, and the finding messages keep `(parts.<p>.forbidden)` until Task 2.
Until Task 2, `profile explain parts.uses.never --rule` answers that the key expands to no rule; no test pins that.

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py:15-48` (scopes)
- Modify: `xarch/modules/spec/domain/key_table.py:8-37, 53, 80, 88, 102, 200, 204`
- Modify: `xarch/architectures/presets/format/keys.yaml` (entries at 154-172, 421-428, after 455, 474-481, after 645,
  1126-1142)
- Modify: `xarch/modules/spec/application/logic/profile_parsing.py:25, 31, 35-39, 85-99, 165, 444-477, 596-599`
- Modify: `xarch/modules/spec/application/logic/profile_needs.py:18-49`
- Modify: `xarch/modules/spec/application/logic/profile_checks.py:30, 45` (docstrings)
- Modify: `xarch/modules/spec/domain/values.py:208` (docstring)
- Modify: `architecture.yaml`, `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml`,
  `tests/bootstrap/corpora/stress.yaml`, `tests/bootstrap/corpora/7cc6111.yaml`, `tests/bootstrap/corpora/df537ca.yaml`
  (key lines only)
- Test: `tests/modules/spec/application/logic/test_forbidden.py` (rewritten helpers, new tests)
- Test: `tests/modules/spec/application/logic/test_profile_needs.py`
- Test: `tests/modules/spec/application/test_explain.py`
- Test: `tests/bootstrap/test_profile_explain.py`
- Edit fixtures/lists: `tests/modules/spec/application/logic/test_profile_parsing.py`,
  `tests/modules/spec/application/logic/test_profile_parsing_tests.py`,
  `tests/modules/spec/application/logic/test_evals.py`, `tests/modules/spec/application/logic/test_looseness.py`,
  `tests/modules/spec/application/logic/test_profile_language.py`,
  `tests/modules/spec/application/logic/test_retired_keys.py`, `tests/modules/spec/application/origins.py`,
  `tests/modules/spec/application/test_origin.py`, `tests/modules/spec/application/test_profile_loading.py`,
  `tests/modules/spec/application/test_check.py`, `tests/bootstrap/test_architecture_files.py`,
  `tests/bootstrap/test_profile_file.py`, `tests/bootstrap/test_presets.py`, `tests/bootstrap/test_needs_agree.py`

**Interfaces:**
- Consumes: `ck.unknown_keys(spec, known, where, scope)`, `keys_of(scope)`, `names_of(scope)` (existing).
- Produces: `PART_USES = "part.uses"`, `TIER_USES = "tier.uses"` in `profile_keys`; `SCOPES[PART_USES] ==
  "parts.<part>.uses"`, `SCOPES[TIER_USES] == "tiers.<tier>.uses"`; key addresses `never`, `parts.<part>.uses`,
  `parts.<part>.uses.never`, `tiers.<tier>.uses`, `tiers.<tier>.uses.apply_never`;
  `profile_parsing._group(value: Any, scope: str, example: str, where: str, problems: list[str]) -> Mapping[Any, Any]`;
  `profile_needs._grouped(mapping, keys, prefix) -> Iterator[tuple[str, Key]]`. `Architecture.forbidden` and
  `Tier.forbidden` are filled exactly as before.

- [ ] **Step 1: Record the baseline**

```bash
mkdir -p /tmp/xarch-2-2
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/baseline-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/baseline-pytest.pid
uv run xarch check > /tmp/xarch-2-2/check.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/check.txt
uv run xarch check --strict > /tmp/xarch-2-2/strict.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/strict.txt
uv run xarch profile check architecture.yaml > /tmp/xarch-2-2/profile-check.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/profile-check.txt
```

When the PID in `/tmp/xarch-2-2/baseline-pytest.pid` has exited, `tail -3 /tmp/xarch-2-2/baseline-pytest.txt`: note
the passed count; every test passes. The three gate files end `exit 0`.

- [ ] **Step 2: Write the failing parser tests**

Replace the whole of `tests/modules/spec/application/logic/test_forbidden.py` with:

```python
"""A part's `uses` group, `uses: {never: <list>}`, naming one of the top-level `never` lists of the calls and modules a
part never uses, and a tier's, `uses: {apply_never: true}`, holding its tests to the list of the part they mirror: each
refused at its address when it is written wrong, and the guards section of the docs saying what the lists hold."""
import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill

DOTTED = "is not a dotted name such as datetime.datetime.now, nor an import name such as socket"
METHOD = f"{DOTTED}, nor a method such as .absolute()"
LISTS = {"pure": ["socket"], "ambient": ["os.getcwd"]}
NO_NAME = "must be the name of a list under `never`"
ONE_LIST = "names one list under never: write the name of a list, such as pure"


def with_list(names, **changes) -> dict:
    """The covered profile with a list `pure` of the names, which the service part names under `uses`."""
    document = covered(never={"pure": names}, **changes)
    document["parts"]["service"]["uses"] = {"never": "pure"}
    return document


def service_uses(uses) -> dict:
    """The covered profile with the lists pure and ambient under `never`, its service part writing `uses` as given."""
    document = covered(never=LISTS)
    document["parts"]["service"]["uses"] = uses
    return document


def unit_uses(uses) -> dict:
    """The covered profile, its unit tier writing `uses` as given."""
    document = covered()
    document["tiers"]["unit"]["uses"] = uses
    return document


@pytest.mark.parametrize("name, problem", [
    pytest.param("datetime..now", f"never.pure: 'datetime..now' {METHOD}", id="a dotted name with an empty step"),
    pytest.param("2fast", f"never.pure: '2fast' {METHOD}", id="a name that starts with a digit"),
    pytest.param(3, f"never.pure: 3 {METHOD}", id="a name that is no text"),
])
def test_a_bad_forbidden_name_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name, problem", [
    pytest.param("open", "never.pure: 'open' is a Python builtin, which a bare name does not ban: write "
                         "builtins.open", id="a bare builtin is rejected with the name to write instead"),
    pytest.param("print", "never.pure: 'print' is a Python builtin, which a bare name does not ban: write "
                          "builtins.print", id="another bare builtin is rejected"),
    pytest.param("__import__", "never.pure: '__import__' is a Python builtin, which a bare name does not ban: "
                               "write builtins.__import__", id="a dunder builtin is rejected"),
])
def test_a_builtin_named_bare_bans_nothing_so_it_is_rejected(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name", [
    pytest.param("builtins.open", id="a builtin written as builtins.<name> is a dotted name"),
    pytest.param("socket", id="a module that is no builtin stays an import name"),
    pytest.param("time", id="a module whose name only resembles a builtin's stays an import name"),
    pytest.param("open.read", id="a dotted name starting with a builtin's is not a bare name"),
    pytest.param("Open", id="a name that differs from a builtin by case is no builtin"),
])
def test_a_name_that_is_no_bare_builtin_is_kept(name):
    assert parsed(with_list([name])).forbidden == {"service": (tuple(name.split(".")),)}


def test_a_method_written_with_a_leading_dot_and_parentheses_is_kept_as_written():
    assert parsed(with_list([".absolute()", "pathlib.Path.cwd"])).forbidden == {
        "service": (("", "absolute()"), ("pathlib", "Path", "cwd"))}


@pytest.mark.parametrize("name, problem", [
    pytest.param(".absolute", "never.pure: '.absolute' is neither a dotted name nor a method: write .absolute() for "
                              "a method called on anything", id="a method without its parentheses"),
    pytest.param("path.absolute()", f"never.pure: 'path.absolute()' {METHOD}", id="a dotted name with parentheses"),
    pytest.param(".a.b()", f"never.pure: '.a.b()' {METHOD}", id="a method of more than one step"),
    pytest.param(".__init__()", "never.pure: '.__init__()' is a special method, which no code calls by name",
                 id="a special method of the language"),
])
def test_a_bad_method_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("uses, problem", [
    pytest.param("pure", "parts.service.uses: must be a mapping {never}, such as {never: pure}",
                 id="a uses that is no mapping"),
    pytest.param([{"never": "pure"}], "parts.service.uses: must be a mapping {never}, such as {never: pure}",
                 id="a uses written as a list"),
    pytest.param({}, "parts.service.uses: says nothing: write never, or drop it", id="a uses that says nothing"),
    pytest.param({"only": ["x"]}, "parts.service.uses: unknown key 'only': use never", id="a key uses does not have"),
    pytest.param({"forbidden": "pure"}, "parts.service.uses: unknown key 'forbidden': use never",
                 id="the old name, under uses"),
    pytest.param({"apply_never": True}, "parts.service.uses: unknown key 'apply_never': use never",
                 id="the switch of a tier, under a part's uses"),
    pytest.param({"never": ["pure", "ambient"]}, f"parts.service.uses.never: {ONE_LIST}", id="a list of list names"),
    pytest.param({"never": ["socket"]}, f"parts.service.uses.never: {ONE_LIST}", id="a list of names"),
    pytest.param({"never": 3}, f"parts.service.uses.never: {NO_NAME}", id="a number"),
    pytest.param({"never": True}, f"parts.service.uses.never: {NO_NAME}", id="true"),
    pytest.param({"never": False}, f"parts.service.uses.never: {NO_NAME}", id="false"),
    pytest.param({"never": None}, f"parts.service.uses.never: {NO_NAME}", id="null"),
    pytest.param({"never": {"pure": True}}, f"parts.service.uses.never: {NO_NAME}", id="a mapping"),
    pytest.param({"never": "nope"}, "parts.service.uses.never: no list named 'nope': use ambient, pure, or write it "
                                    "under `never`", id="a list that is not there"),
])
def test_a_part_s_uses_written_wrong_is_refused_at_its_address(uses, problem):
    assert problems(service_uses(uses)) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("changes", [
    pytest.param({}, id="a file with no never"),
    pytest.param({"never": {}}, id="a never that holds no list"),
])
def test_a_part_naming_a_list_the_file_does_not_hold_is_told_to_write_it_under_never(changes):
    document = layered(**changes)
    document["parts"]["service"]["uses"] = {"never": "pure"}
    assert problems(document) == ["layered.yaml: parts.service.uses.never: no list named 'pure': write it under "
                                  "`never`"]


def test_a_never_that_is_no_mapping_is_the_one_problem_and_the_parts_naming_it_add_none():
    document = service_uses({"never": "nope"})
    document["never"] = ["pure"]
    assert problems(document) == ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such "
                                  "as {pure: [datetime.datetime.now, socket]}"]


def test_a_part_naming_a_list_under_uses_never_uses_its_names_and_a_part_without_uses_none():
    assert parsed(service_uses({"never": "ambient"})).forbidden == {"service": (("os", "getcwd"),)}
    assert parsed(covered(never=LISTS)).forbidden == {}


@pytest.mark.parametrize("uses, problem", [
    pytest.param("yes", "tiers.unit.uses: must be a mapping {apply_never}, such as {apply_never: true}",
                 id="a uses that is no mapping"),
    pytest.param({}, "tiers.unit.uses: says nothing: write apply_never, or drop it", id="a uses that says nothing"),
    pytest.param({"never": True}, "tiers.unit.uses: unknown key 'never': use apply_never",
                 id="never under a tier's uses"),
    pytest.param({"apply_never": "yes-please"}, "tiers.unit.uses.apply_never: must be true or false: whether its "
                                                "tests are held to the `uses.never` list of the part they mirror",
                 id="an apply_never that is no boolean"),
])
def test_a_tier_s_uses_written_wrong_is_refused_at_its_address(uses, problem):
    assert problems(unit_uses(uses)) == [f"layered.yaml: {problem}"]


def test_a_tier_may_hold_its_tests_to_the_list_of_the_part_they_mirror():
    document = with_list(["socket"])
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    assert [tier.forbidden for tier in parsed(document).tiers] == [True, False]


def test_apply_never_false_is_the_same_tier_as_no_uses():
    assert parsed(unit_uses({"apply_never": False})).tiers == parsed(covered()).tiers


def test_the_guards_section_shows_a_method_as_written_and_says_what_it_does_not_see():
    document = with_list([".resolve()", "os.getcwd"])
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`service/`: `.resolve()`, "
        "`os.getcwd`). It catches what is written in the part's own files, through their imports and aliases, and a "
        "method written `.name()` called on anything but the object itself and what it holds; not a name reached "
        "through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def test_the_guards_section_lists_the_names_each_part_may_not_use_and_says_what_it_does_not_see():
    document = covered(never={"clock": ["time.time", "socket"], "printing": ["builtins.print"]})
    document["parts"]["service"]["uses"] = {"never": "clock"}
    document["parts"]["store"]["uses"] = {"never": "clock"}
    document["parts"]["api"]["uses"] = {"never": "printing"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    lines = fill("{{guards}}", parsed(document), "layered.md", file_types=FILE_TYPES).splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`api/`: `builtins.print`; "
        "`service/` and `store/`: `time.time`, `socket`), and neither do the "
        "unit tests of those parts. It catches what is written in the part's own files, through their imports and "
        "aliases, not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")
```

(The two guards-section lines still begin "`forbidden`:"; Task 5 changes the docs line.)

- [ ] **Step 3: Write the failing needs tests**

In `tests/modules/spec/application/logic/test_profile_needs.py`, after `services`, add:

```python
def tiered(**keys) -> dict:
    """layered() in toy, with one tier, unit, that tests every part, its keys the ones given."""
    document = layered(language="toy", testing={"files": ["test_*.py"], "functions": "test_*"}, tiers={"unit": keys})
    for spec in document["parts"].values():
        spec["tests"] = "unit"
    return document


def refusal(address: str, fact: str) -> str:
    return (f"layered.yaml: {address}: its check reads {fact} ({FACTS[fact]}), which the language toy does not "
            f"supply: drop {address}, or check the app with a language whose reader supplies {fact}")
```

and at the end of the file:

```python
def test_a_part_s_never_list_under_uses_needs_the_facts_its_check_reads():
    document = services(uses={"never": "pure"})
    document["never"] = {"pure": ["socket"]}
    assert problems(document, languages=LANGUAGES) == [refusal("parts.service.uses.never", "use"),
                                                       refusal("parts.service.uses.never", "method_call")]


def test_a_tier_that_applies_the_never_lists_needs_the_facts_their_check_reads():
    assert problems(tiered(uses={"apply_never": True}), languages=LANGUAGES) == [
        refusal("tiers.unit.uses.apply_never", "use"), refusal("tiers.unit.uses.apply_never", "method_call")]


def test_apply_never_false_configures_nothing():
    assert parsed(tiered(uses={"apply_never": False}), languages=LANGUAGES).approximate == ()


@pytest.mark.parametrize("uses", [pytest.param("pure", id="a string"), pytest.param([{"never": "pure"}], id="a list")])
def test_a_uses_that_is_no_mapping_configures_nothing_in_any_language(uses):
    document = services(uses=uses)
    assert short(document, {}, TOY) == []
```

In `test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once`, after
`document["tiers"]["unit"]["must_import"] = ["service"]` add:

```python
    document["parts"]["service"]["uses"] = {"never": "pure"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
```

and in `configured`, after `("parts.service.holds", "parts.<part>.holds"),` add
`("parts.service.uses.never", "parts.<part>.uses.never"),`, and after
`("tiers.unit.must_import", "tiers.<tier>.must_import"),` add
`("tiers.unit.uses.apply_never", "tiers.<tier>.uses.apply_never"),`.

- [ ] **Step 4: Write the failing explain tests**

In `tests/modules/spec/application/test_explain.py`, in `SHAPE`, replace the three rows:

```python
    Shown('parts.forbidden', 1, 'the list of names the part may not use', False, True),
```
with
```python
    Shown('parts.uses', 1, "what the part's code uses", False, True),
```
```python
    Shown('forbidden', 0, 'named lists of names a part may not use', False, True),
```
with
```python
    Shown('never', 0, 'named lists of names a part never uses', False, True),
```
```python
    Shown('tiers.apply_forbidden', 1, 'its tests keep to the forbidden list of the part they mirror', False, True),
```
with
```python
    Shown('tiers.uses', 1, 'what its tests keep to of the part they mirror', False, True),
```

At the end of the file add:

```python
def test_the_lists_a_part_never_uses_are_the_top_level_never_and_the_key_never_of_its_uses():
    block, group, held = (explained(address) for address in ("never", "parts.uses", "parts.<part>.uses.never"))
    assert (block.key, block.meaning) == ("never", "named lists of names a part never uses")
    assert "`uses: {never: <list>}`" in block.accepts and block.example.endswith("    uses: {never: pure}\n")
    assert (group.key, group.where, [shown.key for shown in group.keys]) == (
        "parts.uses", "parts.<part>", ["parts.uses.never"])
    assert (held.key, held.where, held.meaning) == (
        "parts.uses.never", "parts.<part>.uses", "the list of names the part never uses")
    assert "the built-in form of a check `may_not` over names used" in held.accepts


def test_a_tier_s_uses_holds_the_switch_that_applies_the_part_s_never_list_to_its_tests():
    group, switch = (explained(address) for address in ("tiers.uses", "tiers.<tier>.uses.apply_never"))
    assert (group.key, [shown.key for shown in group.keys]) == ("tiers.uses", ["tiers.uses.apply_never"])
    assert (switch.key, switch.where, switch.meaning) == (
        "tiers.uses.apply_never", "tiers.<tier>.uses", "its tests keep to the never list of the part they mirror")
    assert switch.accepts.startswith("true or false, a switch and not a list") and '"never apply"' in switch.accepts
    assert "uses: {apply_never: true}" in switch.example


def test_review_never_and_the_top_level_never_each_name_the_other_as_another_list():
    assert "`review.never`" in explained("never").accepts
    assert "the top-level `never`" in explained("review.never").accepts
```

In `tests/bootstrap/test_profile_explain.py`, at the end add:

```python
@pytest.mark.parametrize("address", ["never", "parts.uses", "parts.uses.never", "tiers.uses", "tiers.uses.apply_never",
                                     "review.never"])
def test_never_its_groups_and_review_never_are_explained(address):
    found = runner.invoke(app, ["profile", "explain", address])
    assert (found.exit_code, found.output.splitlines()[0]) == (0, address)
```

- [ ] **Step 5: Run the new tests to see them fail**

Run:
```bash
uv run pytest -q tests/modules/spec/application/logic/test_forbidden.py tests/modules/spec/application/logic/test_profile_needs.py tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py 2>&1 | tail -15
```
Expected: FAIL — the parser refuses `never` and `uses` as unknown keys (`unknown key 'never': use based_on, ...`),
`explained("never")` is an `UnknownKey` with no `.meaning`, and `test_explain` fails on `SHAPE`.

- [ ] **Step 6: The scopes**

In `xarch/modules/spec/domain/profile_keys.py`, after `PART = "part"` add `PART_USES = "part.uses"`, and after
`TIER_DOCS = "tier.docs"` add `TIER_USES = "tier.uses"`. In `SCOPES`, after `PART: "parts.<part>",` add
`PART_USES: "parts.<part>.uses",`, and after `TIER_DOCS: "tiers.<tier>.docs",` add `TIER_USES: "tiers.<tier>.uses",`.

- [ ] **Step 7: The key table**

In `xarch/modules/spec/domain/key_table.py`, add `PART_USES` and `TIER_USES` to the import from
`profile_keys` (alphabetical: `PART_USES` after `PART`, `TIER_USES` after `TIER_DOCS`). Then:

- `Key(PROFILE, "forbidden", rules=("forbidden",)),` becomes `Key(PROFILE, "never", rules=("forbidden",)),`
- `Key(PART, "forbidden", rules=("forbidden",)),` becomes `Key(PART, "uses", opens=PART_USES),`
- after `Key(PART, "folders", rules=("structure",)),` add a line `Key(PART_USES, "never", rules=("forbidden",)),`
  followed by an empty line (the PART block, then its group, then the TIER block)
- `Key(TIER, "apply_forbidden", rules=("forbidden",)),` becomes `Key(TIER, "uses", opens=TIER_USES),`
- after `Key(TIER_DOCS, "helpers", False, False),` add an empty line and `Key(TIER_USES, "apply_never",
  rules=("forbidden",)),`
- in `NEEDS`, `"parts.<part>.forbidden": _FORBIDDEN,` becomes `"parts.<part>.uses.never": _FORBIDDEN,` and
  `"tiers.<tier>.apply_forbidden": _FORBIDDEN,` becomes `"tiers.<tier>.uses.apply_never": _FORBIDDEN,`.

The resulting part block ends:

```python
    Key(PART, "libraries", rules=("libraries",)),
    Key(PART, "uses", opens=PART_USES),
    Key(PART, "tests", rules=("tiers",)),
    Key(PART, "untested"),
    Key(PART, "package_only", rules=("package-only",)),
    Key(PART, "folders", rules=("structure",)),

    Key(PART_USES, "never", rules=("forbidden",)),

    Key(TIER, "proves", False, False),
    Key(TIER, "litmus", False, False),
    Key(TIER, "uses", opens=TIER_USES),
```

and the tier docs block ends:

```python
    Key(TIER_DOCS, "helpers", False, False),

    Key(TIER_USES, "apply_never", rules=("forbidden",)),

    Key(TESTING, "files", True, rules=("tiers", "test-tree")),
```

- [ ] **Step 8: The texts of `keys.yaml`, in the order of the table**

In `xarch/architectures/presets/format/keys.yaml`:

Replace the entry `forbidden:` (from `  forbidden:` through `          forbidden: pure`, lines 154-172) with:

```yaml
  never:
    meaning: named lists of names a part never uses
    accepts: >-
      a map {<list>: [<dotted name>, ...]}; a part points to one list with `uses: {never: <list>}`. An entry is a dotted
      name as an absolute import binds it (`datetime.datetime.now`; a builtin as `%namespace%.open`, a bare `open` is
      refused), a whole package (`socket`), or a method written with a leading dot and parentheses (`.absolute()`). A
      file may not import a listed package or anything below it, nor use a listed name, called or not, as the file
      writes it (through the import that binds it, or a builtin by its bare name where nothing shadows it), nor call a
      listed method on anything no import names (a variable, a parameter, the result of a call), but on the method's own
      object and what it holds (`self.paths.resolve()`: a port's or its own). A method entry matches any object with a
      method of that name, so it belongs only in a list of parts that never call one legitimately. Silent on a name
      reached through a variable or `getattr`, a method of an object the list does not name, an annotation, and what a
      helper in another file does: a ban list, not a proof of purity. Not `review.never`, the files review never sends,
      which is another list
    example: |
      never:
        pure: [time.time, socket]
        ambient: [pathlib.Path.cwd, .absolute()]
      <<part>>
          uses: {never: pure}
```

Replace the entry `parts.<part>.forbidden:` (lines 421-428) with:

```yaml
  parts.<part>.uses:
    meaning: what the part's code uses
    accepts: "a map {never}: `never` names the list under the top-level `never` of what the part's code never uses"
    example: |
      never:
        pure: [time.time, socket]
      <<part>>
          uses: {never: pure}
```

After the entry `parts.<part>.folders:` (its last line is `            schemas: the table definitions`), before
`  tiers.<tier>.proves:`, insert:

```yaml
  parts.<part>.uses.never:
    meaning: the list of names the part never uses
    accepts: >-
      the name of one list under the top-level `never`: no file of the part uses a name the list holds, by an import or
      in its code, a module, a dotted name or a method; the built-in form of a check `may_not` over names used. It names
      code, not the parts the part may import, which `may_import` says
    example: |
      never:
        pure: [time.time, socket]
      <<part>>
          uses: {never: pure}
```

Replace the entry `tiers.<tier>.apply_forbidden:` (lines 474-481) with:

```yaml
  tiers.<tier>.uses:
    meaning: what its tests keep to of the part they mirror
    accepts: "a map {apply_never}: `apply_never: true` holds its tests to the `uses.never` list of the part they mirror"
    example: |
      <<testing>>
      tiers:
        unit:
          uses: {apply_never: true}
      <<tiered-part>>
```

After the entry `tiers.<tier>.docs.helpers:` (the last `tiers.<tier>.docs.*` entry), before `  testing.files:`, insert:

```yaml
  tiers.<tier>.uses.apply_never:
    meaning: its tests keep to the never list of the part they mirror
    accepts: >-
      true or false, a switch and not a list: true holds the tier's tests to the `uses.never` list of the part they
      mirror (it applies the part's never list to them as well; it does not read as "never apply"); false is the same as
      leaving it out
    example: |
      <<testing>>
      tiers:
        unit:
          uses: {apply_never: true}
      <<tiered-part>>
```

In the entry `review.never:`, the last two lines of `accepts` become:

```yaml
      the same path twice. `profile check` lists a path the profile it is compared with holds that this one does not as
      looser. Not the top-level `never`, the names a part never uses, which is another list
```

Check: `grep -n "forbidden" xarch/architectures/presets/format/keys.yaml` prints only the line of
`evals.placement.alike` (Task 4 changes it).

- [ ] **Step 9: The parser**

In `xarch/modules/spec/application/logic/profile_parsing.py`:

Docstring, line 25:
```
        uses: {never: <list>}  the name of a list under the top-level `never`, which the part never uses
```
line 31:
```
    never: {<list>: [<name>, ...]}             named lists of what a part never uses
```
line 35 (and the description below it gains the group):
```
    tiers: {<tier>: {proves, litmus, uses, types_only, folder, may_import, may_also_import, docs}}
                               the kinds of test, in the order their litmus tests run. A tier with a `folder` below
                               the tests folder says in `may_import` what the tests there may import; `may_also_import`
                               what each of its tests may also import beyond that or what the part it mirrors may;
                               `uses: {apply_never: true}` holds its tests to the `uses.never` list of the part they
                               mirror; `docs` holds what only fills the generated docs
```
(Keep the existing words of that description; the only change is the `uses` clause before `docs`. Wrap at 120.)

Import `PART_USES` and `TIER_USES` in the block `from xarch.modules.spec.domain.profile_keys import (...)`
(alphabetical, `PART_USES` after `PART`, `TIER_USES` after `TIER_DOCS`).

In `parse_profile`, line 165:
```python
    lists = _forbidden_lists(document["never"], problems, language) if "never" in document else {}
```

Replace `_forbidden_lists` and `_forbidden_refs` (lines 444-477) with:

```python
def _forbidden_lists(value: Any, problems: list[str],
                     language: Language) -> dict[str, tuple[tuple[str, ...], ...] | None] | None:
    """The named lists of names a part never uses; a list already reported is None. None: `never` is no mapping."""
    if not isinstance(value, Mapping):
        problems.append("never: must be a mapping of list names to lists of dotted names, such as "
                        "{pure: [datetime.datetime.now, socket]}")
        return None
    lists: dict[str, tuple[tuple[str, ...], ...] | None] = {}
    for name, names in value.items():
        if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
            problems.append(f"never: {name!r} is not a list name: use letters, digits, '_' and '-'")
        else:
            lists[name] = ck.forbidden_names(names, f"never.{name}", problems, language)
    return lists


def _forbidden_refs(specs: dict[str, Any], parts: dict[str, Part],
                    lists: dict[str, tuple[tuple[str, ...], ...] | None] | None,
                    problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    """What each part whose `uses` names a list under `never` never uses; when `never` is no mapping, a part's list
    says nothing more."""
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name in parts:
        spec = specs[name]
        if "uses" not in spec:
            continue
        uses = _group(spec["uses"], PART_USES, "{never: pure}", f"parts.{name}.uses", problems)
        if "never" not in uses or lists is None:
            continue
        ref, where = uses["never"], f"parts.{name}.uses.never"
        if isinstance(ref, list):
            problems.append(f"{where}: names one list under never: write the name of a list, such as pure")
        elif not isinstance(ref, str):
            problems.append(f"{where}: must be the name of a list under `never`")
        elif ref not in lists:
            use = f"use {', '.join(sorted(lists))}, or write it" if lists else "write it"
            problems.append(f"{where}: no list named {ref!r}: {use} under `never`")
        elif lists[ref] is not None:
            forbidden[name] = lists[ref]
    return forbidden


def _group(value: Any, scope: str, example: str, where: str, problems: list[str]) -> Mapping[Any, Any]:
    """What a group of keys a part or a tier opens holds, such as `uses`: {} when it is no mapping or says nothing, each
    said at where; its unknown keys are refused under its own scope."""
    names = ", ".join(key.name for key in keys_of(scope))
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{{names}}}, such as {example}")
        return {}
    if not value:
        problems.append(f"{where}: says nothing: write {names}, or drop it")
        return {}
    problems += ck.unknown_keys(value, names_of(scope), where, scope)
    return value
```

In `_tier`, replace the read of `apply_forbidden` (lines 596-599):

```python
    held = spec.get("apply_forbidden", False)
    if not isinstance(held, bool):
        problems.append(f"{where}.apply_forbidden: must be true or false: whether its tests are held to the "
                        "`forbidden` list of the part they mirror")
```
with
```python
    uses = _group(spec["uses"], TIER_USES, "{apply_never: true}", f"{where}.uses", problems) if "uses" in spec else {}
    held = uses.get("apply_never", False)
    if not isinstance(held, bool):
        problems.append(f"{where}.uses.apply_never: must be true or false: whether its tests are held to the "
                        "`uses.never` list of the part they mirror")
```

- [ ] **Step 10: The needs walker**

In `xarch/modules/spec/application/logic/profile_needs.py`, replace `_configured` with:

```python
def _configured(document: Mapping[Any, Any], presets: Mapping[str, Any]) -> Iterator[tuple[str, Key]]:
    """Each key the document sets that needs facts, with its address in the file, in the order of the file's scopes:
    the file, its parts, its tiers, its testing (a preset by what the preset holds), its guards, each with the keys of
    its own map that need facts and are set, a part's and a tier's then those of each group one of its keys opens
    (`uses`)."""
    yield from _set(document, keys_of(PROFILE), "")
    for scope, held in ((PART, "parts"), (TIER, "tiers")):
        entries = document.get(held)
        for name, value in entries.items() if isinstance(entries, Mapping) else ():
            if isinstance(value, Mapping):
                yield from _set(value, keys_of(scope), f"{held}.{name}.")
                yield from _grouped(value, keys_of(scope), f"{held}.{name}.")
    testing = document.get("testing")
    testing = presets.get(testing) if isinstance(testing, str) else testing
    if isinstance(testing, Mapping):
        yield from _set(testing, keys_of(TESTING), "testing.")
    guards = document.get("guards")
    for key in keys_of(GUARD) if isinstance(guards, Mapping) else ():
        if key.name in guards:
            yield f"guards.{key.name}", key
            held = guards[key.name]
            for nested in _guard_keys(key.name) if isinstance(held, Mapping) else ():
                if nested.needs and held.get(nested.name) not in (None, False):
                    yield f"guards.{key.name}.{nested.name}", nested
```

and after `_set` add:

```python
def _grouped(mapping: Mapping[Any, Any], keys: tuple[Key, ...], prefix: str) -> Iterator[tuple[str, Key]]:
    """The keys that need facts set in each group a key of the mapping opens, one level down, such as a part's
    `uses`; a group that is no mapping sets none."""
    for key in keys:
        group = mapping.get(key.name)
        if key.opens and isinstance(group, Mapping):
            yield from _set(group, keys_of(key.opens), f"{prefix}{key.name}.")
```

- [ ] **Step 11: Docstrings that name the key**

- `xarch/modules/spec/application/logic/profile_checks.py:30`: `"""How a method in a `never` list, called on anything,
  ends: `.absolute()`."""`
- `profile_checks.py:45`: `"""The name of the method an item of a `never` list names, `.<name>()`; None when it names
  none."""`
- `xarch/modules/spec/domain/values.py:208`: `    forbidden: its tests are held to the `uses.never` list of the part
  they mirror`

- [ ] **Step 12: The profiles' key lines**

```bash
sed -i -E 's/^    forbidden: ([A-Za-z0-9_-]+)$/    uses: {never: \1}/; s/^forbidden:$/never:/; s/^    apply_forbidden: true$/    uses: {apply_never: true}/' \
  architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml \
  tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
grep -c 'uses: {never:' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
grep -c 'uses: {apply_never: true}' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
grep -n 'forbidden' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
```

Expected counts of `uses: {never:`: 14, 11, 11, 10, 5, 8; of `uses: {apply_never: true}`: 2, 1, 1, 3, 1, 1. The last
grep prints only the prose lines of `cli.yaml` (18, 32, 48, 173, 191, 225) and `web.yaml` (18, 32, 48, 175, 193,
227), each naming `` `forbidden` `` in backticks: Task 5 changes them with the docs. `git diff --stat` shows the lists'
entries untouched (each file only its key lines). Read `git diff -- architecture.yaml`: every change is one
`forbidden:`/`apply_forbidden:` line.

- [ ] **Step 13: The fixtures and lists of the existing tests**

Each edit below is exact; nothing else in these files changes.

`tests/modules/spec/application/logic/test_profile_parsing.py`:
- lines 45-46 become:
  ```python
        "layered.yaml: unknown keys 'colour', 'extra': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
        "hints, language, layers, name, never, parts, reserved, review, testing, tiers"]
  ```
- lines 164-165 become:
  ```python
                 ["layered.yaml: parts.x: unknown key 'colour': use built_by, folders, holds, immutable, libraries, litmus, "
                  "may_import, must_import, names, no_callbacks, package_only, path, role, shared, tests, types_only, untested, uses"],
  ```
- lines 389-424 become:
  ```python
  def test_a_part_refers_to_a_list_of_forbidden_names_by_its_name():
      document = layered(never={"pure": ["datetime.datetime.now", "builtins.open", "socket"]})
      document["parts"]["service"]["uses"] = {"never": "pure"}
      document["parts"]["shared"]["uses"] = {"never": "pure"}
      forbidden = parsed(document).forbidden
      assert forbidden == {"service": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",)),
                           "shared": (("datetime", "datetime", "now"), ("builtins", "open"), ("socket",))}


  def test_a_part_that_names_no_list_forbids_nothing():
      assert parsed(layered(never={"pure": ["socket"]})).forbidden == {}


  @pytest.mark.parametrize("never, part, expected", [
      pytest.param(3, "pure", ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such "
                               "as {pure: [datetime.datetime.now, socket]}"], id="not a mapping"),
      pytest.param({"pure": []}, "pure", ["layered.yaml: never.pure: must be a non-empty list of dotted names or "
                                          "import names, such as [datetime.datetime.now, socket]"], id="an empty list"),
      pytest.param({"pure": ["open"]}, "pure", ["layered.yaml: never.pure: 'open' is a Python builtin, which a bare "
                                                "name does not ban: write builtins.open"], id="a bare builtin"),
      pytest.param({"pure": ["socket", "socket"]}, "pure", ["layered.yaml: never.pure: 'socket' is listed twice"],
                   id="a name twice"),
      pytest.param({"a b": ["socket"]}, "pure", ["layered.yaml: never: 'a b' is not a list name: use letters, "
                                                 "digits, '_' and '-'",
                                                 "layered.yaml: parts.service.uses.never: no list named 'pure': write "
                                                 "it under `never`"], id="a bad list name"),
      pytest.param({"pure": ["socket"]}, "impure", ["layered.yaml: parts.service.uses.never: no list named 'impure': "
                                                    "use pure, or write it under `never`"], id="no such list"),
      pytest.param({"pure": ["socket"]}, 3, ["layered.yaml: parts.service.uses.never: must be the name of a list "
                                             "under `never`"], id="a part naming no text"),
  ])
  def test_bad_forbidden_lists_are_refused(never, part, expected):
      document = layered(never=never)
      document["parts"]["service"]["uses"] = {"never": part}
      assert problems(document) == expected
  ```
- lines 447-448 become:
  ```python
          "layered.yaml: unknown keys 'colour', 'layout': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
          "hints, language, layers, name, never, parts, reserved, review, testing, tiers",
  ```

`tests/modules/spec/application/logic/test_profile_parsing_tests.py`:
- lines 128-130 become:
  ```python
      document = covered(never={"pure": ["socket"]})
      document["parts"]["service"]["uses"] = {"never": "pure"}
      document["tiers"]["unit"]["uses"] = {"apply_never": True}
  ```
- lines 172-174 become:
  ```python
      pytest.param({"colour": 1}, "layered.yaml: tiers.unit: unknown key 'colour': use docs, folder, litmus, "
                                  "may_also_import, may_import, must_import, plain_tables, proves, types_only, "
                                  "uses", id="an unknown key"),
  ```
- lines 181-183 become:
  ```python
      pytest.param({"uses": {"apply_never": "yes"}}, "layered.yaml: tiers.unit.uses.apply_never: must be true or false: "
                                                     "whether its tests are held to the `uses.never` list of the part "
                                                     "they mirror", id="apply_never that is no boolean"),
  ```
- lines 301-302 become:
  ```python
  PART_KEYS = ("built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
               "package_only, path, role, shared, tests, types_only, untested, uses")
  ```
- lines 347-348 become:
  ```python
          "layered.yaml: tiers.unit: unknown key 'tier': use docs, folder, litmus, may_also_import, may_import, "
          "must_import, plain_tables, proves, types_only, uses"]
  ```

`tests/modules/spec/application/logic/test_retired_keys.py`, lines 44-48 become:
```python
PART_USE = ("built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
            "package_only, path, role, shared, tests, types_only, untested, uses")
TIER_USE = "docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses"
PROFILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, "
               "parts, reserved, review, testing, tiers")
```

`tests/modules/spec/application/logic/test_evals.py`:
- lines 200-202 become:
  ```python
      document = alike(("store", "shared"), store={"uses": {"never": "pure"}, "holds": "functions", "immutable": True},
                       shared={"uses": {"never": "same"}, "holds": "functions", "immutable": True})
      document["never"] = {"pure": ["time.time"], "same": ["time.time"]}
  ```
- lines 246-247 become:
  ```python
      document = alike(("store", "shared"), store={"uses": {"never": "pure"}}, shared={"uses": {"never": "ambient"}})
      document["never"] = {"pure": ["time.time"], "ambient": ["os.getcwd"]}
  ```
- line 250: `    document["parts"]["shared"].pop("uses")`
  (The messages `differ in forbidden` stay until Task 4.)

`tests/modules/spec/application/logic/test_looseness.py`:
- line 65: `    custom = {**BASE, "parts": parts, "never": {"pure": ["socket"]},`
- line 67: `                        | {"uses": {"apply_never": False}, "may_also_import": ["edge"]}},`
- line 167: `             "never": {"pure": ["socket"]}, "testing": {**TESTING, "skips": ["pytest.mark.skip"]},`
- line 169: `                       | {"uses": {"apply_never": False}, "may_also_import": ["edge"]}},`
  (The expected `Loosened` keys and sentences stay until Task 4.)

`tests/modules/spec/application/logic/test_profile_language.py`, lines 48-50 become:
```python
    assert problems(layered(never={"pure": ["writeln"]}, parts={
        **layered()["parts"], "shared": {"path": "shared", "role": "r", "uses": {"never": "pure"}}}), languages=BOTH) == [
        "layered.yaml: never.pure: 'writeln' is a Pascal builtin, which a bare name does not ban: write system.writeln"]
```

`tests/modules/spec/application/origins.py`, lines 4-5 and 10:
```python
TIER = {"proves": "a rule", "litmus": "Does it call a rule?", "uses": {"apply_never": True}, "types_only": ["store"]}
PARTS = {"core": {"path": "core", "role": "rules", "may_import": [], "uses": {"never": "pure"}, "tests": "unit"},
```
```python
BASE = {"name": "base", "parts": PARTS, "never": {"pure": ["time.time", "socket"]},
```

`tests/modules/spec/application/test_origin.py`:
- line 36: `    custom = {**BASE, "parts": parts, "never": {"pure": ["socket"]},`
- line 38: `                        | {"uses": {"apply_never": False}, "may_also_import": ["edge"]}},`
- lines 61-62:
  ```python
      custom = {**BASE, "parts": part("store", may_import=[]) | part("core", uses={"never": "pure"}),
                "never": {"pure": ["time", "socket"]}}
  ```

`tests/modules/spec/application/test_profile_loading.py`, lines 14 and 17:
```python
    "core": {"path": "core", "role": "rules", "uses": {"never": "pure"}},
```
```python
    "never": {"pure": ["socket"]}}
```

`tests/modules/spec/application/test_check.py`, lines 30-31:
```python
                     Problem("load", "mine.yaml: unknown key 'colour': use based_on, checks, docs, evals, excluded, fakes, files, "
                                     "guards, hints, language, layers, name, never, parts, reserved, review, testing, tiers"),
```

`tests/bootstrap/test_architecture_files.py`:
- lines 145-146:
  ```python
      pytest.param('xarch: 2', ["unknown key 'xarch': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
                                "hints, language, layers, name, never, parts, reserved, review, testing, tiers",
  ```
- line 148: `    pytest.param('name: [a]\nparts: [1]\nnever: x\nlayers: 3\ntiers: 4\nfakes: 5\nguards: 6\n'`
- line 151: `                  'never: must be a mapping of list names to lists of dotted names, such as '`
- lines 183-185:
  ```python
      pytest.param('name: n\nparts: {a: {path: a, role: r, uses: {never: l}}}\nnever: {l: [open]}\n',
                   ["never.l: 'open' is a Python builtin, which a bare name does not ban: write builtins.open"],
                   id='a bare builtin in a never list'),
  ```
- lines 231-233:
  ```python
                   ["parts.a: unknown key 'tier': renamed in 0.3.0: write tests; use built_by, folders, holds, "
                    "immutable, libraries, litmus, may_import, must_import, names, no_callbacks, package_only, path, "
                    "role, shared, tests, types_only, untested, uses",
  ```
- lines 237-238:
  ```python
                   ["unknown keys 'rules', 'xarch2': use based_on, checks, docs, evals, excluded, fakes, files, guards, hints, "
                    "language, layers, name, never, parts, reserved, review, testing, tiers"],
  ```

`tests/bootstrap/test_profile_file.py`:
- `PROFILE` lines 17-18 become `never:` / `  pure: [builtins.print]`, and line 23 `    uses: {never: pure}`
- lines 103-104:
  ```python
          f"{tmp_path / 'small.yaml'}: unknown key 'xarch': use based_on, checks, docs, evals, excluded, fakes, files, "
          "guards, hints, language, layers, name, never, parts, reserved, review, testing, tiers",)
  ```
  (Line 82's expected message keeps `(parts.core.forbidden)` until Task 2.)

`tests/bootstrap/test_presets.py`, `PROFILE` lines 13 and 20: `never:` and `    uses: {never: nothing_printed}`
(line 76's rule `"forbidden"` stays until Task 2).

`tests/bootstrap/test_needs_agree.py`, `EVERY_KEY`: `    forbidden: pure` becomes `    uses: {never: pure}`, the
top-level `forbidden:` becomes `never:`, and `    apply_forbidden: true` becomes `    uses: {apply_never: true}`.

- [ ] **Step 14: Run the task's tests**

Run:
```bash
uv run pytest -q tests/modules/spec tests/bootstrap/test_profile_explain.py tests/bootstrap/test_architecture_files.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_presets.py tests/bootstrap/test_needs_agree.py tests/bootstrap/test_bundled_guards.py tests/bootstrap/test_bundled_tiers.py 2>&1 | tail -5
```
Expected: all pass. `test_key_catalogue.py` and `test_profile_keys.py` (logic) pass: the texts follow the table's
order, every example loads and uses its key, and the unknown-key message under `parts.<part>.uses` and
`tiers.<tier>.uses` names `never` and `apply_never`.

- [ ] **Step 15: The whole suite**

```bash
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/task1-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/task1-pytest.pid
```
When it has exited, `tail -5 /tmp/xarch-2-2/task1-pytest.txt`: all passed, including `test_recorded_corpora.py`
(the profiles load into the same `Architecture`, so the recorded findings, which still say `forbidden`, are found as
recorded) and `test_docs_templates.py` (the golden docs do not move: only key lines changed). Then
`uv run ruff check` and `uv run xarch check`: both clean.

- [ ] **Step 16: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py xarch/modules/spec/domain/key_table.py \
  xarch/architectures/presets/format/keys.yaml xarch/modules/spec/application/logic/profile_parsing.py \
  xarch/modules/spec/application/logic/profile_needs.py xarch/modules/spec/application/logic/profile_checks.py \
  xarch/modules/spec/domain/values.py architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml \
  tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml tests
git status --short
git commit -m "$(cat <<'EOF'
A part names the list it never uses with uses: {never: <list>}, under the top-level block never, and a tier holds its tests to it with uses: {apply_never: true}: two scopes opened by a key uses, their key table rows and keys.yaml entries, the parser's messages, the needs walker one level into the group, the six profiles' key lines and every test fixture; the rule id and the findings' words are unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

`git status --short` before the commit shows no `.claude/` and no `docs/superpowers/` path staged.

---

### Task 2: The rule id `never-use`, and the keys the check names

**Files:**
- Modify: `xarch/kernel/violations.py:10`
- Modify: `xarch/modules/spec/domain/key_table.py` (the three rows Task 1 added with `rules=("forbidden",)`)
- Modify: `xarch/modules/rules/application/logic/expansion.py:49-67, 354, 367`
- Modify: `xarch/modules/rules/application/services/source_check.py:90`
- Modify: `README.md:358`
- Modify (by the script below): `tests/bootstrap/corpora/df537ca.json`, `tests/bootstrap/corpora/stress-7cc6111.json.xz`
- Test: `tests/kernel/test_violations.py`, `tests/modules/spec/application/logic/test_hints.py`,
  `tests/modules/spec/application/logic/test_written_checks.py`, `tests/modules/spec/application/test_explain.py`,
  `tests/modules/rules/application/logic/test_forbidden.py`, `tests/modules/rules/application/logic/test_expansion.py`,
  `tests/modules/rules/application/logic/test_explained.py`, `tests/modules/rules/application/logic/test_sentences.py`,
  `tests/modules/rules/application/logic/checks.py`, `tests/modules/rules/builders.py` (docstring),
  `tests/bootstrap/test_forbidden.py`, `tests/bootstrap/test_profile_file.py`, `tests/bootstrap/test_check_json.py`,
  `tests/bootstrap/test_presets.py`, `tests/bootstrap/test_rule_ids.py`, `tests/bootstrap/test_profile_explain_words.py`
- Throwaway: `/tmp/xarch-2-2/recorded.py`

**Interfaces:**
- Consumes: the key addresses of Task 1.
- Produces: `RULES` with `"never-use"` third; `expansion.book(profile)["never-use"]` (the group renamed from
  `"forbidden"`); rule keys `parts.<p>.uses.never` and `parts.<p>.uses.never; tiers.<t>.uses.apply_never`;
  `expansion.KEYS` holding `"parts.uses.never", "tiers.uses.apply_never"` third and fourth.

- [ ] **Step 1: Write the failing tests**

`tests/kernel/test_violations.py:36-39`, the sorted list loses `"forbidden"` and gains `"never-use"` after `"names"`:
```python
    assert sorted(RULES) == ["built-by", "closed-tree", "cycles", "dead-code", "holds", "immutable", "libraries",
                             "must-import", "names", "never-use", "no-callbacks", "no-comments", "no-duplicates",
                             "no-twins", "package-only", "pass-through", "private-imports", "rules", "scenario-coverage",
                             "shared", "stand-ins", "structure", "syntax", "test-tree", "tiers", "types-only"]
```

`tests/modules/spec/application/logic/test_hints.py:22`:
```python
KNOWN = ("built-by, closed-tree, cycles, dead-code, holds, immutable, libraries, must-import, names, never-use, no-callbacks, "
```
(the two following lines unchanged).

`tests/modules/spec/application/logic/test_written_checks.py`, at the end:
```python
def test_a_check_of_its_own_may_not_take_the_id_never_use_and_may_take_forbidden_which_xarch_no_longer_has():
    taken, free = read({"never-use": SMALL}), read({"forbidden": SMALL})
    assert taken == ({}, ["checks.never-use: never-use is the id of a check xarch has: give your check an id of its "
                          "own, such as my-never-use"])
    assert (list(free[0]), free[1]) == (["forbidden"], [])


def test_a_hint_for_a_check_of_its_own_named_forbidden_is_the_hint_of_that_check():
    architecture = parsed(layered(checks={"forbidden": SMALL}, hints={"forbidden": "see the docs"}))
    assert (list(architecture.checks), architecture.hints) == (["forbidden"], {"forbidden": "see the docs"})
```

`tests/modules/spec/application/test_explain.py`, at the end:
```python
def test_the_keys_of_never_feed_the_rule_never_use():
    assert [explained(address).rules for address in ("never", "parts.uses.never", "tiers.uses.apply_never")] == [
        ("never-use",)] * 3
```

`tests/bootstrap/test_profile_explain_words.py`, at the end:
```python
def test_a_part_s_never_list_and_a_tier_s_switch_expand_to_the_rules_never_use():
    listed = explain("parts.uses.never", "--rule", "--profile", "web")
    assert listed.exit_code == 0, listed.output
    assert listed.output.splitlines()[0] == "parts.uses.never expands to 22 rules in web, written as checks:"
    assert "  never-use-domain:" in listed.output
    switch = explain("tiers.uses.apply_never", "--rule", "--profile", "web")
    assert switch.output.splitlines()[0] == "tiers.uses.apply_never expands to 11 rules in web, written as checks:"
```

Messages and rule ids of the tests that pin them, by sed (each file holds only finding messages of this check in
parentheses of this form):
```bash
sed -i -E 's/\(parts\.([a-z_-]+)\.forbidden; tiers\.([a-z_-]+)\.apply_forbidden\)/(parts.\1.uses.never; tiers.\2.uses.apply_never)/g; s/\(parts\.([a-z_-]+)\.forbidden\)/(parts.\1.uses.never)/g' \
  tests/modules/rules/application/logic/test_forbidden.py tests/bootstrap/test_forbidden.py \
  tests/bootstrap/test_profile_file.py tests/bootstrap/test_check_json.py
grep -n "forbidden" tests/modules/rules/application/logic/test_forbidden.py tests/bootstrap/test_forbidden.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_check_json.py
```
The grep then shows the rule ids, docstrings and names left; edit these by hand:
- `tests/modules/rules/application/logic/test_forbidden.py:66`: `    assert (found.rule, found.fix) == ("never-use", "do what needs datetime.datetime.now outside domain/, and hand "`
- `tests/bootstrap/test_check_json.py:40`: `        {"rule": "never-use", "file": "app/modules/docs/domain/clock.py", "line": 1,`
- `tests/bootstrap/test_check_json.py:102`: `        ("rules", "the layers are in docs/project/architecture.md"), ("never-use", None)]`
- the docstrings, the `forbidden=` fields of domain values, the helper `violations`/`forbidden` and the test names
  stay (internal names, step 2.4).

Other tests:
- `tests/bootstrap/test_presets.py:76`: `    pytest.param(b"print('loaded')\n", "never-use", id="a name the part forbids"),`
- `tests/bootstrap/test_rule_ids.py:39-40`:
  ```python
      pytest.param({"kernel/x.py": "import socket\n"}, {}, "never-use",
                   "do what needs socket outside kernel/, and hand kernel/ the result", id="never-use"),
  ```
- `tests/modules/rules/application/logic/test_expansion.py:42-44`:
  ```python
      pytest.param("never-use", ["never-use: app/domain read imported-name, use, method-call may_not path",
                                 "never-use: tests/domain/unit where not below fakes read imported-name, use, method-call "
                                 "may_not path"], id="never-use"),
  ```
- `tests/modules/rules/application/logic/test_explained.py:89-90, 94`:
  ```python
      both = Rule("never-use", Scope(part="store"), ("use",), MAY_NOT, (Match("path", names=(("x",),)),),
                  (Saying("m", "f"),), key="parts.store.uses.never; tiers.unit.uses.apply_never")
  ```
  ```python
      assert keyed(rules, "tiers.uses.apply_never") == [both]
  ```
- `tests/modules/rules/application/logic/test_sentences.py:31, 42`: the key `"parts.domain.forbidden"` becomes
  `"parts.domain.uses.never"` in both places.
- `tests/modules/rules/application/logic/checks.py:31`: `    return checked(expansion.book(profile)["never-use"], profile, app, tests)`
- `tests/modules/rules/builders.py:6`: "held to `forbidden`" becomes "held to `uses.never`".

- [ ] **Step 2: Run them to see them fail**

```bash
uv run pytest -q tests/kernel/test_violations.py tests/modules/spec/application/logic/test_hints.py tests/modules/spec/application/logic/test_written_checks.py tests/modules/spec/application/test_explain.py tests/modules/rules tests/bootstrap/test_forbidden.py tests/bootstrap/test_profile_file.py tests/bootstrap/test_check_json.py tests/bootstrap/test_presets.py tests/bootstrap/test_rule_ids.py tests/bootstrap/test_profile_explain_words.py 2>&1 | tail -20
```
Expected: FAIL — `RULES` still holds `forbidden`, `book(...)` has no key `never-use` (`KeyError: 'never-use'`), the
messages end `(parts.domain.forbidden)`, a check named `never-use` loads and one named `forbidden` is refused.

- [ ] **Step 3: The rule id and the engine**

`xarch/kernel/violations.py:10`:
```python
RULES = ("rules", "libraries", "never-use", "tiers", "types-only", "cycles", "package-only", "scenario-coverage",
```

`xarch/modules/spec/domain/key_table.py`: the three rows become `Key(PROFILE, "never", rules=("never-use",)),`,
`Key(PART_USES, "never", rules=("never-use",)),`, `Key(TIER_USES, "apply_never", rules=("never-use",)),`.

`xarch/modules/rules/application/logic/expansion.py`, `_forbidden` becomes:
```python
def _forbidden(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part with a `uses.never` list neither imports what it names, nor uses a name it lists, nor calls a
    method it lists on anything but what its object holds; a test of a tier that applies the lists
    (`uses.apply_never`) is held to the list of each part it mirrors. One finding per line and name."""
    if not profile.forbidden:
        return ()
    facts = ("imported-name", "use", "method-call")
    keep, exempt = _all("not relative", "not on-own-object"), _all("reported-at-import")
    fakes = (_of(f"not below {'/'.join(profile.fakes.folder)}"),) if profile.fakes is not None else ()
    found = [Rule("never-use", Scope(APP, part), facts, MAY_NOT, (Match("path", names=names),),
                  (Saying("{where} may not {verb} {hit} ({key})", FORBIDDEN_FIX, once=("line", "hit")),),
                  keep=keep, exempt=exempt, key=f"parts.{part}.uses.never")
             for part, names in profile.forbidden.items()]
    found += [Rule("never-use", Scope(TESTS, part, tier.name, fakes), facts, MAY_NOT, (Match("path", names=names),),
                   (Saying("a test of {scope_part}/ ({tier} tier) may not {verb} {hit} ({key})", FORBIDDEN_FIX,
                           once=("line", "hit")),),
                   keep=keep, exempt=exempt, key=f"parts.{part}.uses.never; tiers.{tier.name}.uses.apply_never")
              for tier in profile.tiers if tier.forbidden for part, names in profile.forbidden.items()]
    return tuple(found)
```
`KEYS` (line 354), first line:
```python
KEYS = ("parts.may_import", "parts.libraries", "parts.uses.never", "tiers.uses.apply_never", "tiers", "tiers.may_also_import",
```
`book` (line 367): `"forbidden": _forbidden(profile),` becomes `"never-use": _forbidden(profile),`.

`xarch/modules/rules/application/services/source_check.py:90`: `        found += run(book["never-use"], facts, rules)`.

`README.md:358`, the rule id list the README test pins:
```
  rule, else `null`. `rule` is one of: `rules`, `libraries`, `never-use`, `tiers` (a test's imports, or a test in no
```

- [ ] **Step 4: Run the tests of Step 2**

Same command as Step 2. Expected: PASS.

- [ ] **Step 5: See the recorded corpora fail**

```bash
uv run pytest -q tests/bootstrap/test_recorded_corpora.py 2>&1 | tail -8
```
Expected: FAIL for `df537ca` and the stress corpus, the first difference a finding whose rule is `never-use` (found)
against `forbidden` (recorded).

- [ ] **Step 6: The script that edits the recordings by text**

Create `/tmp/xarch-2-2/recorded.py`:

```python
"""The findings of rule forbidden in a recording, by their text: the rule becomes never-use and the key at the end of
the message names uses.never (and uses.apply_never); every other line stays as it is. Prints how many it changed."""
import lzma
import re
import sys
from pathlib import Path

KEY = re.compile(r"\(parts\.([A-Za-z0-9_-]+)\.forbidden(?:; tiers\.([A-Za-z0-9_-]+)\.apply_forbidden)?\)\",$")


def renamed(match: re.Match) -> str:
    tier = f"; tiers.{match[2]}.uses.apply_never" if match[2] else ""
    return f'(parts.{match[1]}.uses.never{tier})",'


def edited(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    count = 0
    for i, line in enumerate(lines):
        if line == '"forbidden",' and lines[i - 1] in ('"V",', '"W",') and lines[i - 2] == "[":
            message = KEY.sub(renamed, lines[i + 3])
            assert message != lines[i + 3], lines[i + 3]
            lines[i], lines[i + 3] = '"never-use",', message
            count += 1
    return "\n".join(lines), count


path = Path(sys.argv[1])
if path.suffix == ".xz":
    with lzma.open(path, "rt", encoding="utf-8") as file:
        text, count = edited(file.read())
    with lzma.open(path, "wt", encoding="utf-8") as file:
        file.write(text)
else:
    text, count = edited(path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")
print(f"{path.name}: {count} findings")
```

It reads each finding as the recordings lay it out (`[`, kind, rule, file, line, message, fix, `]`, one per line) and
touches only the rule line of a finding whose rule is `forbidden` and that finding's message line.

- [ ] **Step 7: Run it and read the diff line by line**

```bash
xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz > /tmp/xarch-2-2/stress-before.json
python3 -I /tmp/xarch-2-2/recorded.py tests/bootstrap/corpora/df537ca.json
python3 -I /tmp/xarch-2-2/recorded.py tests/bootstrap/corpora/stress-7cc6111.json.xz
git diff --stat -- tests/bootstrap/corpora/df537ca.json
git diff -- tests/bootstrap/corpora/df537ca.json | grep '^[-+]"' | sort | uniq -c | sort -rn
xz -dc tests/bootstrap/corpora/stress-7cc6111.json.xz | diff /tmp/xarch-2-2/stress-before.json - | grep '^[<>]' | sort | uniq -c | sort -rn
```
Expected: `df537ca.json: 21 findings` and `stress-7cc6111.json.xz: 23 findings`. The df537ca diff is 42 lines out
and 42 in: 21 `"forbidden",` become `"never-use",`, and 21 messages lose `(parts.services.forbidden)` for
`(parts.services.uses.never)`. The stress diff: 23 `"forbidden",` become `"never-use",`; 22 messages end
`(parts.<p>.uses.never)`; one reads `a test of controller/ (integration tier) may not use pathlib.Path.cwd
(parts.controller.uses.never; tiers.integration.uses.apply_never)`. No other line moves: the findings naming
`xarch.modules.rules.application.logic.forbidden`, `forbidden_names` and the `file` fields `test_forbidden.py` stay.
`git diff -- tests/bootstrap/corpora/7cc6111.json tests/bootstrap/corpora/examples-cli.json tests/bootstrap/corpora/examples-web.json`
prints nothing. The order of findings needs no move: the recordings are sorted by file, line and rule, and the only
other rule at a renamed finding's file and line is `built-by` (`import_check.py:104` in the stress recording), which
sorts before both `forbidden` and `never-use`; check it:
```bash
python3 -I - <<'EOF'
import json, lzma
for name, found in (("df537ca", json.load(open("tests/bootstrap/corpora/df537ca.json"))["findings"]),
                    ("stress", json.load(lzma.open("tests/bootstrap/corpora/stress-7cc6111.json.xz", "rt"))["findings"])):
    near = {(f[2], f[3]) for f in found if f[1] == "never-use"}
    print(name, sorted({f[1] for f in found if (f[2], f[3]) in near and f[1] != "never-use"}))
EOF
```
Expected: `df537ca []` and `stress ['built-by']`.

- [ ] **Step 8: Run the recorded corpora and the README test**

```bash
uv run pytest -q tests/bootstrap/test_recorded_corpora.py tests/architecture/test_readme.py 2>&1 | tail -3
```
Expected: PASS.

- [ ] **Step 9: The whole suite**

```bash
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/task2-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/task2-pytest.pid
```
When it has exited: all passed (`test_needs_agree.py` now asks `parts.uses.never` and `tiers.uses.apply_never` with
`--rule` and finds their needs agree; `test_expandable.py` finds `KEYS` in the book's order). `uv run ruff check`,
`uv run xarch check`: clean.

- [ ] **Step 10: Commit**

```bash
git add xarch/kernel/violations.py xarch/modules/spec/domain/key_table.py xarch/modules/rules/application/logic/expansion.py \
  xarch/modules/rules/application/services/source_check.py README.md tests \
  tests/bootstrap/corpora/df537ca.json tests/bootstrap/corpora/stress-7cc6111.json.xz
git status --short
git commit -m "$(cat <<'EOF'
The check of a part's never list has the rule id never-use, in findings, JSON and hints, and its findings end with the key they come from, (parts.<p>.uses.never) or (parts.<p>.uses.never; tiers.<t>.uses.apply_never); profile explain --rule expands parts.uses.never and tiers.uses.apply_never; a check of the profile's own may take the id forbidden and not never-use; the recorded findings of rule forbidden are edited by text to the new rule and key, nothing else moved

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: The old and misplaced names are refused

**Files:**
- Modify: `xarch/modules/spec/domain/profile_keys.py:154` (`RETIRED`)
- Test: `tests/modules/spec/domain/test_profile_keys.py`, `tests/modules/spec/application/logic/test_retired_keys.py`,
  `tests/modules/spec/application/logic/test_forbidden.py`, `tests/modules/spec/application/test_explain.py`,
  `tests/bootstrap/test_profile_explain.py`, `tests/bootstrap/test_architecture_files.py`

**Interfaces:**
- Consumes: `retired(scope, name)`, `retired_at(address)`, `ck.unknown_keys`, `ck.rule_hints` (step 1); `RULES`
  without `forbidden` (Task 2); `PART_USES` (Task 1).
- Produces: `RETIRED`, the seven entries of the Global Constraints.

- [ ] **Step 1: Write the failing tests**

`tests/modules/spec/domain/test_profile_keys.py`: the docstring's last clause becomes "it holds the part key tier,
renamed tests, the old names of never and its keys, and those keys written outside uses"; the import becomes
`from xarch.modules.spec.domain.profile_keys import HELD, PART, PROFILE, RETIRED, RULE_ID, SCOPES, TIER, Retired`;
replace `test_the_one_name_retired_is_the_part_key_tier_renamed_tests` with:

```python
def test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses():
    assert RETIRED == (
        Retired(PART, "tier", "renamed in 0.3.0: write tests"),
        Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
        Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
        Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
        Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
        Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
        Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"))
```

`tests/modules/spec/application/logic/test_retired_keys.py`: add `PART_USES` to the import from `profile_keys`
(after `PART`), and replace `test_the_shipped_table_retires_the_part_key_tier_alone` with:

```python
TESTS = "renamed in 0.3.0: write tests"
LIST_MOVED = "moved in 0.3.0: write uses: {never: <list>}"
SWITCH_MOVED = "moved in 0.3.0: write uses: {apply_never: true}"
BLOCK = "renamed in 0.3.0: write never"
RULE = "renamed in 0.3.0: write never-use"
LIST_OUTSIDE = "a key of uses: write uses: {never: <list>}"
SWITCH_OUTSIDE = "a key of uses: write uses: {apply_never: true}"


@pytest.mark.parametrize("scope, name, text", [
    pytest.param(PART, "tier", TESTS, id="the part key tier"),
    pytest.param(PART, "forbidden", LIST_MOVED, id="the part key forbidden"),
    pytest.param(TIER, "apply_forbidden", SWITCH_MOVED, id="the tier key apply_forbidden"),
    pytest.param(PROFILE, "forbidden", BLOCK, id="the block forbidden"),
    pytest.param(RULE_ID, "forbidden", RULE, id="the rule id forbidden"),
    pytest.param(PART, "never", LIST_OUTSIDE, id="never on a part"),
    pytest.param(TIER, "apply_never", SWITCH_OUTSIDE, id="apply_never on a tier"),
    pytest.param(PART_USES, "never", "", id="never under a part's uses, a key"),
    pytest.param(TIER, "forbidden", "", id="forbidden under a tier, only unknown"),
    pytest.param(TIER, "tier", "", id="tier under a tier"),
    pytest.param(SCENARIO_COVERAGE, "tier", "", id="the tier of scenario-coverage"),
    pytest.param(PART, "tests", "", id="the part key tests"),
])
def test_the_shipped_table_answers_each_name_in_its_scope(scope, name, text):
    assert retired(scope, name) == text


@pytest.mark.parametrize("address, text", [
    pytest.param("parts.tier", TESTS, id="parts.tier"),
    pytest.param("parts.<part>.tier", TESTS, id="parts.<part>.tier"),
    pytest.param("forbidden", BLOCK, id="forbidden"),
    pytest.param("parts.forbidden", LIST_MOVED, id="parts.forbidden"),
    pytest.param("parts.<part>.forbidden", LIST_MOVED, id="parts.<part>.forbidden"),
    pytest.param("tiers.apply_forbidden", SWITCH_MOVED, id="tiers.apply_forbidden"),
    pytest.param("tiers.<tier>.apply_forbidden", SWITCH_MOVED, id="tiers.<tier>.apply_forbidden"),
    pytest.param("parts.never", LIST_OUTSIDE, id="parts.never"),
    pytest.param("tiers.apply_never", SWITCH_OUTSIDE, id="tiers.apply_never"),
    pytest.param("parts.uses.never", "", id="parts.uses.never"),
    pytest.param("tiers.uses.apply_never", "", id="tiers.uses.apply_never"),
    pytest.param("never", "", id="never"),
    pytest.param("review.never", "", id="review.never"),
])
def test_the_shipped_table_answers_each_address_profile_explain_is_typed_with(address, text):
    assert retired_at(address) == text
```

`tests/modules/spec/application/logic/test_forbidden.py`: add `from xarch.kernel.violations import RULES` to the
imports, and after `unit_uses` add:

```python
PART_USE = ("built_by, folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
            "package_only, path, role, shared, tests, types_only, untested, uses")
TIER_USE = "docs, folder, litmus, may_also_import, may_import, must_import, plain_tables, proves, types_only, uses"
FILE_USE = ("based_on, checks, docs, evals, excluded, fakes, files, guards, hints, language, layers, name, never, parts, "
            "reserved, review, testing, tiers")
LIST_MOVED = "moved in 0.3.0: write uses: {never: <list>}"
SWITCH_MOVED = "moved in 0.3.0: write uses: {apply_never: true}"
LIST_OUTSIDE = "a key of uses: write uses: {never: <list>}"
SWITCH_OUTSIDE = "a key of uses: write uses: {apply_never: true}"
NO_TIER = "no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"


def service_writing(**keys) -> dict:
    """The covered profile with the lists pure and ambient under `never`, its service part writing the keys given."""
    document = covered(never=LISTS)
    document["parts"]["service"] |= keys
    return document
```

and at the end of the file:

```python
def test_a_part_writing_forbidden_is_told_the_list_moved_under_uses():
    assert problems(service_writing(forbidden="pure")) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]


def test_the_list_a_part_wrote_under_forbidden_is_in_no_problem():
    found = problems(service_writing(forbidden="secret-list"))
    assert found == [f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]
    assert not any("secret-list" in problem for problem in found)


def test_a_part_writing_never_outside_uses_is_told_it_is_a_key_of_uses():
    assert problems(service_writing(never="pure")) == [
        f"layered.yaml: parts.service: unknown key 'never': {LIST_OUTSIDE}; use {PART_USE}"]


def test_apply_never_under_a_part_s_uses_is_only_unknown_there():
    assert problems(service_writing(uses={"never": "pure", "apply_never": True})) == [
        "layered.yaml: parts.service.uses: unknown key 'apply_never': use never"]


def test_a_part_of_an_old_profile_writing_forbidden_and_tier_gets_both_in_sorted_order_then_no_tier_tests_it():
    document = service_writing(forbidden="pure", tier="unit")
    document["parts"]["service"].pop("tests")
    assert problems(document) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.service: unknown key 'tier': renamed in 0.3.0: write tests; use {PART_USE}",
        f"layered.yaml: parts.service: {NO_TIER}"]


def test_a_part_writing_forbidden_beside_uses_is_refused_for_forbidden_and_its_uses_read_as_written():
    assert problems(service_writing(forbidden="pure", uses={"never": "nope"})) == [
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        "layered.yaml: parts.service.uses.never: no list named 'nope': use ambient, pure, or write it under `never`"]


def test_a_tier_writing_apply_forbidden_is_told_the_switch_moved_under_uses():
    document = covered()
    document["tiers"]["unit"]["apply_forbidden"] = True
    assert problems(document) == [
        f"layered.yaml: tiers.unit: unknown key 'apply_forbidden': {SWITCH_MOVED}; use {TIER_USE}"]


def test_a_tier_writing_apply_never_outside_uses_is_told_it_is_a_key_of_uses():
    document = covered()
    document["tiers"]["unit"]["apply_never"] = True
    assert problems(document) == [
        f"layered.yaml: tiers.unit: unknown key 'apply_never': {SWITCH_OUTSIDE}; use {TIER_USE}"]


def test_a_file_writing_the_block_forbidden_is_told_it_is_renamed_never_and_its_parts_once_each():
    document = covered(forbidden=LISTS)
    document["parts"]["service"]["forbidden"] = "pure"
    document["parts"]["store"]["forbidden"] = "pure"
    assert problems(document) == [
        f"layered.yaml: unknown key 'forbidden': renamed in 0.3.0: write never; use {FILE_USE}",
        f"layered.yaml: parts.service: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}",
        f"layered.yaml: parts.store: unknown key 'forbidden': {LIST_MOVED}; use {PART_USE}"]


@pytest.mark.parametrize("never, after", [
    pytest.param(LISTS, [], id="a never that loads adds no problem"),
    pytest.param(["pure"], ["layered.yaml: never: must be a mapping of list names to lists of dotted names, such as "
                            "{pure: [datetime.datetime.now, socket]}"], id="a never written wrong adds its own"),
])
def test_a_file_writing_forbidden_beside_never_is_refused_for_forbidden_and_never_read_as_written(never, after):
    document = service_uses({"never": "pure"}) | {"forbidden": LISTS, "never": never}
    assert problems(document) == [
        f"layered.yaml: unknown key 'forbidden': renamed in 0.3.0: write never; use {FILE_USE}", *after]


def test_a_hint_for_the_rule_id_forbidden_is_told_it_is_renamed_never_use():
    assert problems(layered(hints={"forbidden": "see the docs"})) == [
        "layered.yaml: hints.forbidden: unknown rule id 'forbidden': renamed in 0.3.0: write never-use; use "
        f"{', '.join(sorted(RULES))}"]
```

`tests/modules/spec/application/test_explain.py`, at the end:

```python
@pytest.mark.parametrize("address, key, text", [
    pytest.param("forbidden", "forbidden", "renamed in 0.3.0: write never", id="the old block"),
    pytest.param("parts.forbidden", "parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}",
                 id="the old part key"),
    pytest.param("parts.<part>.forbidden", "parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}",
                 id="the old part key with its placeholder"),
    pytest.param("tiers.apply_forbidden", "tiers.apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}",
                 id="the old tier key"),
    pytest.param("tiers.<tier>.apply_forbidden", "tiers.apply_forbidden",
                 "moved in 0.3.0: write uses: {apply_never: true}", id="the old tier key with its placeholder"),
    pytest.param("parts.never", "parts.never", "a key of uses: write uses: {never: <list>}", id="never on a part"),
    pytest.param("tiers.apply_never", "tiers.apply_never", "a key of uses: write uses: {apply_never: true}",
                 id="apply_never on a tier"),
])
def test_an_old_or_misplaced_name_of_never_is_refused_with_its_fixed_text(address, key, text):
    found = explained(address)
    assert (type(found), found.key, found.retired) == (UnknownKey, key, text)
```

`tests/bootstrap/test_profile_explain.py`, at the end:

```python
@pytest.mark.parametrize("address, text", [
    pytest.param("forbidden", "renamed in 0.3.0: write never", id="the old block"),
    pytest.param("parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}", id="the old part key"),
    pytest.param("tiers.apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}", id="the old tier key"),
    pytest.param("parts.never", "a key of uses: write uses: {never: <list>}", id="never on a part"),
    pytest.param("tiers.apply_never", "a key of uses: write uses: {apply_never: true}", id="apply_never on a tier"),
])
def test_an_old_name_of_never_is_refused_with_its_text_exit_2_and_retired_in_json(address, text):
    said = runner.invoke(app, ["profile", "explain", address])
    assert said.exit_code == 2
    assert f"error: no key `{address}` in the format: {text}; the nearest are " in said.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] == text
```

`tests/bootstrap/test_architecture_files.py`, in the parametrised list of `test_a_bad_file_raises_...`, after the
case `id='a part still writing tier'`, add:

```python
    pytest.param('name: n\nnever: {pure: [socket]}\nparts: {a: {path: a, role: r, forbidden: secret-list}}\n',
                 ["parts.a: unknown key 'forbidden': moved in 0.3.0: write uses: {never: <list>}; use built_by, "
                  "folders, holds, immutable, libraries, litmus, may_import, must_import, names, no_callbacks, "
                  "package_only, path, role, shared, tests, types_only, untested, uses"],
                 id='a part still writing forbidden'),
```

- [ ] **Step 2: Run them to see them fail**

```bash
uv run pytest -q tests/modules/spec/domain/test_profile_keys.py tests/modules/spec/application/logic/test_retired_keys.py tests/modules/spec/application/logic/test_forbidden.py tests/modules/spec/application/test_explain.py tests/bootstrap/test_profile_explain.py tests/bootstrap/test_architecture_files.py 2>&1 | tail -15
```
Expected: FAIL — `RETIRED` holds one entry; the refusals read `unknown key 'forbidden': use ...` with no hint; the
explain answers have `retired == ""`. (`test_apply_never_under_a_part_s_uses_is_only_unknown_there` already passes:
it guards that no entry under `PART_USES` is added.)

- [ ] **Step 3: The table**

In `xarch/modules/spec/domain/profile_keys.py`, `RETIRED` becomes:

```python
RETIRED: tuple[Retired, ...] = (
    Retired(PART, "tier", "renamed in 0.3.0: write tests"),
    Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
    Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
    Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
    Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
    Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
    Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"),
)
```

- [ ] **Step 4: Run the tests of Step 2**

Same command. Expected: PASS. Then
`grep -rn '== "forbidden"\|== "apply_forbidden"\|== "never"\|"apply_never" in\|"forbidden" in' xarch`
prints nothing (no code tests for an old name).

- [ ] **Step 5: The whole suite**

```bash
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/task3-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/task3-pytest.pid
```
When it has exited: all passed. `uv run ruff check`: clean.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/domain/profile_keys.py tests
git status --short
git commit -m "$(cat <<'EOF'
The table of retired names holds the old names of never: a part's forbidden and a tier's apply_forbidden are told they moved under uses, the block forbidden and the rule id forbidden that they are renamed never and never-use, and never on a part or apply_never on a tier that it is a key of uses; one problem each, the value never shown, and profile explain answers each address with exit 2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: `where`, `Loosened`, `alike`, the check language and the agent prose name the new keys

**Files:**
- Modify: `xarch/cli/reports/where_report.py:61-62, 80-81, 114, 120, 134`
- Modify: `xarch/modules/spec/application/logic/looseness.py:11-13, 34-35, 70, 87, 152-153, 166-167`
- Modify: `xarch/modules/spec/domain/published.py:92, 97` (docstring of `Loosened`)
- Modify: `xarch/modules/spec/application/logic/evals.py:6, 61, 152`
- Modify: `xarch/architectures/presets/format/keys.yaml` (`evals.placement.alike`, near 1192)
- Modify: `xarch/modules/rules/domain/vocabulary.py:347`
- Modify: `xarch/architectures/agents.md:58`
- Test: `tests/cli/reports/test_where_report.py`, `tests/bootstrap/test_where.py`,
  `tests/modules/spec/application/logic/test_looseness.py`, `tests/modules/spec/application/test_origin.py`,
  `tests/bootstrap/test_check_enforcement.py`, `tests/modules/spec/application/logic/test_evals.py`,
  `tests/modules/rules/domain/test_vocabulary.py`

**Interfaces:**
- Consumes: the profiles of Task 1 (`web.yaml` writes `    uses: {apply_never: true}` once).
- Produces: `where` JSON field `never_uses` (no field `forbidden`), text label `never uses`; `LOOSER` keys
  `"uses.never"`, `"uses.apply_never"`; `evals._RULED == ("uses.never", "holds", "immutable")`.

- [ ] **Step 1: Write the failing tests**

`tests/cli/reports/test_where_report.py`: imports become
```python
import json
from dataclasses import replace

from xarch.cli.reports.where_report import where_document, where_lines
from xarch.modules.rules.contract import InPart, InTests, PartShown, Ungoverned, Untested
```
and at the end:
```python
def test_the_names_a_part_never_uses_are_a_line_of_their_own_and_the_field_never_uses():
    held = replace(PART, forbidden=("socket", "builtins.open"))
    assert where_lines(held)[6] == "never uses:     socket, builtins.open"
    document = json.loads(where_document("custom", held))
    assert document["never_uses"] == ["socket", "builtins.open"] and "forbidden" not in document


def test_a_test_held_to_the_list_of_the_part_it_mirrors_shows_it_under_the_same_label_and_field():
    test = InTests("tests/cli/test_app.py", True, PART.part, (), "contract", (), ("socket",), None, False, "", "", "")
    assert "never uses:     socket" in where_lines(test)
    document = json.loads(where_document("custom", test))
    assert document["never_uses"] == ["socket"] and "forbidden" not in document


def test_an_answer_that_is_no_part_gives_never_uses_empty():
    document = json.loads(where_document("custom", Ungoverned("app/odd.py", False, (), None, "")))
    assert document["never_uses"] == [] and "forbidden" not in document
```

`tests/bootstrap/test_where.py`: line 47 `    assert found["never uses"].startswith("datetime.datetime.now, datetime.datetime.utcnow")`;
line 117 `    assert found["libraries"] == [] and "builtins.open" in found["never_uses"] and "forbidden" not in found`.

`tests/modules/spec/application/logic/test_looseness.py`, lines 74 and 78-79:
```python
        Loosened("uses.never", "core", "time.time", "core no longer forbids time.time (parts.core.uses.never)"),
```
```python
        Loosened("uses.apply_never", "unit", "",
                 "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"),
```
`tests/modules/spec/application/test_origin.py`, lines 50 and 54-55: the same two replacements.

`tests/bootstrap/test_check_enforcement.py`, after
`test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_shown_and_never_fails_strict`, add:
```python
def test_a_custom_profile_whose_tier_no_longer_applies_the_never_lists_is_looser_under_uses_apply_never(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    assert text.count("    uses: {apply_never: true}\n") == 1
    (tmp_path / "arch/mine.yaml").write_text(text.replace("    uses: {apply_never: true}\n", ""))
    document = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)
    assert document["enforcement"]["profile"]["looser"] == [
        {"key": "uses.apply_never", "part": "unit", "what": "",
         "sentence": "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"}]
```

`tests/modules/spec/application/logic/test_evals.py`: `NOT_ALIKE` (lines 206-207) becomes
```python
NOT_ALIKE = ("check tells them apart by rule, so one file is not all that tells them apart: write the same uses.never, "
             "holds and immutable for each, or drop the group")
```
and in `test_parts_that_forbid_different_things_are_not_alike` both `differ in forbidden` become `differ in uses.never`.

`tests/modules/rules/domain/test_vocabulary.py`, at the end:
```python
def test_the_variable_key_is_shown_with_a_key_of_the_profile_as_a_profile_writes_it_now():
    key = next(variable for variable in VARIABLES if variable.name == "key")
    assert key.meaning == "the key of the profile the check comes from: parts.store.uses.never, checks.<id>"
```

- [ ] **Step 2: Run them to see them fail**

```bash
uv run pytest -q tests/cli/reports/test_where_report.py tests/bootstrap/test_where.py tests/modules/spec/application/logic/test_looseness.py tests/modules/spec/application/test_origin.py tests/bootstrap/test_check_enforcement.py tests/modules/spec/application/logic/test_evals.py tests/modules/rules/domain/test_vocabulary.py 2>&1 | tail -15
```
Expected: FAIL — `KeyError: 'never_uses'`, the label `may not use:`, `Loosened("forbidden", ...)`, `differ in
forbidden`, the old example of `key`.

- [ ] **Step 3: `where`**

`xarch/cli/reports/where_report.py`: both `lines.append(_line("may not use", ", ".join(where.forbidden)))` become
`lines.append(_line("never uses", ", ".join(where.forbidden)))`; in `where_document`, the default
`"forbidden": [],` becomes `"never_uses": [],`, and both `"forbidden": list(where.forbidden)` become
`"never_uses": list(where.forbidden)`.

- [ ] **Step 4: `Loosened`**

`xarch/modules/spec/application/logic/looseness.py`:
- docstring line 11: "a name the bundled `uses.never` list of a part holds that no entry of the custom list covers";
  line 13: "a tier no longer `uses.apply_never`".
- `LOOSER`:
  ```python
  LOOSER = ("may_import", "libraries", "uses.never", "must_import", "untested", LITMUS, "types_only", "may_also_import",
            "uses.apply_never", "testing.skips", "files.pinned", "reserved", "known", "translated", "review.never",
            "review.mask", "evals.placement.lines")
  ```
- line 70: `        found += [("uses.never", name, ".".join(banned)) for banned in base.forbidden.get(name, ())`
- line 87: `    found += [("uses.apply_never", tier.name, "") for tier in base.tiers`
- `_sentence`:
  ```python
          case "uses.never":
              return f"{part} no longer forbids {what} (parts.{part}.uses.never)"
  ```
  ```python
          case "uses.apply_never":
              return f"the {part} tests are no longer held to their part's never list (tiers.{part}.uses.apply_never)"
  ```

`xarch/modules/spec/domain/published.py`, the docstring of `Loosened`:
```
        uses.never      part no longer forbids what
```
```
        uses.apply_never the tests of tier part are no longer held to their part's never list
```

- [ ] **Step 5: `alike`**

`xarch/modules/spec/application/logic/evals.py`: docstring line 6 "group alike in what `check` holds them to by
`uses.never`, `holds` and `immutable`)"; `_RULED = ("uses.never", "holds", "immutable")`; line 152
`"uses.never, holds and immutable for each, or drop the group")`.

`xarch/architectures/presets/format/keys.yaml`, `evals.placement.alike`, the line near 1192 becomes:
```yaml
      naming a part twice, a part in two groups, and parts that differ in `uses.never`, `holds` or `immutable`
```
(if it now passes 120 columns, move its last words to the start of the next line; the loaded text is one line either
way). Then `grep -n "forbidden" xarch/architectures/presets/format/keys.yaml` prints nothing.

- [ ] **Step 6: The check language and the agent prose**

`xarch/modules/rules/domain/vocabulary.py:347`:
```python
    Variable("key", "the key of the profile the check comes from: parts.store.uses.never, checks.<id>",
```
`xarch/architectures/agents.md:58`:
```
- Do not switch a guard off, and do not loosen the profile, its `may_import`, `libraries` or `uses.never` entries.
```

- [ ] **Step 7: Run the tests of Step 2, then the suite**

Same command as Step 2: PASS. Then:
```bash
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/task4-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/task4-pytest.pid
```
When it has exited: all passed. `uv run ruff check`: clean.

- [ ] **Step 8: Commit**

```bash
git add xarch/cli/reports/where_report.py xarch/modules/spec/application/logic/looseness.py \
  xarch/modules/spec/domain/published.py xarch/modules/spec/application/logic/evals.py \
  xarch/architectures/presets/format/keys.yaml xarch/modules/rules/domain/vocabulary.py xarch/architectures/agents.md tests
git status --short
git commit -m "$(cat <<'EOF'
where prints never uses: and its JSON field is never_uses, the Loosened keys are uses.never and uses.apply_never in text and JSON with sentences naming the new addresses, a group of alike parts that differ in their list is told they differ in uses.never, the variable key's example is parts.store.uses.never, and the agent instructions name uses.never

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: The generated docs

**Files:**
- Modify: `xarch/modules/spec/application/logic/docs_template.py:34, 461`
- Modify: `xarch/architectures/testing.md:225`
- Modify: `xarch/architectures/cli.yaml`, `xarch/architectures/web.yaml` (the prose naming `` `forbidden` ``)
- Regenerate: `docs/cli/*.md`, `docs/web/*.md`, `docs/xarch/*.md` (all of them, by the script)
- Test: `tests/modules/spec/application/logic/test_forbidden.py`, `tests/bootstrap/test_bundled_guards.py`
- Throwaway: `/tmp/xarch-2-2/regenerate_docs.py`

**Interfaces:**
- Consumes: everything above. Produces: no new name.

- [ ] **Step 1: Write the failing tests**

`tests/modules/spec/application/logic/test_forbidden.py`, in both guards-section tests the expected line begins
`"- \`never-use\`: a part neither imports nor uses by name what its \`uses.never\` list names ("` in place of
`"- \`forbidden\`: a part neither imports nor uses by name what is listed for it ("`:
```python
    assert lines[3] == (
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`service/`: "
        "`.resolve()`, `os.getcwd`). It catches what is written in the part's own files, through their imports and "
        "aliases, and a method written `.name()` called on anything but the object itself and what it holds; not a name "
        "reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")
```
```python
    assert lines[3] == (
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`api/`: "
        "`builtins.print`; `service/` and `store/`: `time.time`, `socket`), and neither do the "
        "unit tests of those parts. It catches what is written in the part's own files, through their imports and "
        "aliases, not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")
```
`tests/bootstrap/test_bundled_guards.py:80`:
```python
        "- `never-use`: a part neither imports nor uses by name what its `uses.never` list names (`domain/`, "
```

- [ ] **Step 2: Run them to see them fail**

```bash
uv run pytest -q tests/modules/spec/application/logic/test_forbidden.py tests/bootstrap/test_bundled_guards.py 2>&1 | tail -8
```
Expected: FAIL, the line begins "- `forbidden`: a part neither imports nor uses by name what is listed for it".

- [ ] **Step 3: The template and the prose**

`xarch/modules/spec/application/logic/docs_template.py:34`: "what each part may not use (with `uses.never`)".
`docs_template.py:461`:
```python
    return (f"`never-use`: a part neither imports nor uses by name what its `uses.never` list names ({listed}){tests}. It "
```
(if the line passes 120 columns, break the f-string after `{tests}. ` into two literals; the text is unchanged).

`xarch/architectures/testing.md:225`: "a `forbidden` name dropped" becomes "a `uses.never` name dropped", and "a tier
that lost a `types_only` part or its `apply_forbidden`" becomes "a tier that lost a `types_only` part or its
`uses.apply_never`". Nothing else on the line changes.

The prose of the two bundled profiles:
```bash
sed -i 's/ to its `forbidden` list/ to its `uses.never` list/; s/checked by `forbidden` for/checked by `uses.never` for/' \
  xarch/architectures/cli.yaml xarch/architectures/web.yaml
grep -nw 'forbidden\|apply_forbidden' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
awk 'length > 120 {print FILENAME": "FNR}' xarch/architectures/cli.yaml xarch/architectures/web.yaml
```
Expected: the grep prints nothing; the awk prints nothing (the longest edited line is 119 columns).

- [ ] **Step 4: Regenerate the golden docs and read the diff**

Create `/tmp/xarch-2-2/regenerate_docs.py`:

```python
"""Write every doc of docs/{cli,web,xarch} from the bundled profiles and xarch's own architecture.yaml."""
import sys
from pathlib import Path

from xarch.bootstrap.wiring import build_controllers

root = Path(sys.argv[1])
for folder, profile in (("cli", "cli"), ("web", "web"), ("xarch", str(root / "architecture.yaml"))):
    for file in build_controllers().spec.docs(profile).files:
        target = root / "docs" / folder / "/".join(file.path)
        if target.suffix == ".md" and target.exists():
            target.write_text(file.template, encoding="utf-8")
print("written")
```

Run:
```bash
uv run python -I /tmp/xarch-2-2/regenerate_docs.py "$PWD"
git status --short -- docs
git diff --stat -- docs
git diff -U0 -- docs | grep '^@@'
```

Expected moved files: `docs/cli/testing.md`, `docs/web/testing.md`, `docs/xarch/testing.md`,
`docs/cli/architecture.md`, `docs/web/architecture.md`; nothing new is untracked. Expected moved lines:
`docs/cli/testing.md` 33 (the unit tier's "may touch", "checked by `uses.never`"), 341 (the rule line, now
"`never-use`: ... what its `uses.never` list names"), 370 (the enforcement paragraph); `docs/web/testing.md` 33, 342,
371; `docs/xarch/testing.md` 157 (the rule line); the litmus lines of `docs/cli/architecture.md` (368, 479, 499, 601,
604) and `docs/web/architecture.md` (370, 481, 501, 603, 606), "holds it to its `uses.never` list". Read every hunk:
each changes only those words. `docs/xarch/architecture.md` does not move ("anything not listed is forbidden" and
`forbidden_imports` stay). Any other moved line is a bug of this step: do not hand-edit it; restore with
`git checkout -- docs/cli docs/web docs/xarch` and report the hunk.

- [ ] **Step 5: Run the docs tests, then the suite**

```bash
uv run pytest -q tests/bootstrap/test_docs_templates.py tests/modules/spec/application/logic/test_forbidden.py tests/bootstrap/test_bundled_guards.py 2>&1 | tail -3
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/task5-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/task5-pytest.pid
```
Expected: PASS; when the suite has exited, all passed. `uv run ruff check`: clean.

- [ ] **Step 6: Commit**

```bash
git add xarch/modules/spec/application/logic/docs_template.py xarch/architectures/testing.md \
  xarch/architectures/cli.yaml xarch/architectures/web.yaml docs/cli docs/web docs/xarch tests
git status --short
git commit -m "$(cat <<'EOF'
The generated testing doc's rule line reads never-use: a part neither imports nor uses by name what its uses.never list names, the enforcement paragraph names a uses.never name dropped and a tier's uses.apply_never, and the bundled profiles' prose holds a part to its uses.never list; the golden docs are regenerated and only those lines moved

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: README, CHANGELOG and the gates

**Files:**
- Modify: `README.md:117-120, 271, 296, 328-329, 365-366, 409-410, 475, 507, 527, 730, 1036`
- Modify: `CHANGELOG.md` (`## [Unreleased]` / `### Changed`)

**Interfaces:**
- Consumes: everything above. Produces: nothing new in code.

- [ ] **Step 1: README**

Each line below replaces the line of the same number (the rule id list at 358 was done in Task 2):

117:
```
parts*:   {<part>: {path*, role*, litmus, may_import, must_import, libraries, uses: {never}, tests | untested,
```
119:
```
never:    {<list>: [<dotted name> | .<method>(), ...]}        layers: {<chain>: [<part>, ...]}
```
120:
```
tiers:    {<tier>: {proves, litmus, uses: {apply_never}, plain_tables, types_only, folder, may_import, may_also_import,
```
271:
```
| `never-use` | a name or module a part (or, with `uses.apply_never`, its tests) may not use, or a method written `.name()` it may not call on anything but its own object and what that holds | `never`, `parts.uses.never`, `tiers.uses.apply_never` |
```
296: "`forbidden` or `tiers`)" becomes "`never` or `tiers`)".
328-329:
```
    {"rule": "never-use", "file": "app/modules/docs/domain/clock.py", "line": 1,
     "message": "domain/ of modules/docs may not import socket (parts.domain.uses.never)",
```
365: "`{"key", "part", "what", "sentence"}` with `key` one of `may_import`, `libraries`, `uses.never`, `untested`,"
366: "`types_only`, `may_also_import`, `uses.apply_never`, `testing.skips`, ..." (the rest of the line unchanged).
409: "name of its `uses.never` list no entry covers any more, ..." (the rest unchanged).
410: "... a tier no longer `uses.apply_never`, ..." (the rest unchanged).
475: "a list, or `any outside package`), the names it never uses (`never uses`, from its `uses.never`), and the tier
that tests it with the" (rewrap the paragraph's next line only if the line passes 120 columns).
507:
```
  "never_uses": ["datetime.datetime.now", "builtins.open"],
```
527: "  not check them; `never_uses` the dotted names the part never uses (its `uses.never`)."
730: "one group at most; the parts of a group must have the same `uses.never`, `holds` and `immutable`, since parts
`check`".
1036: "`may_import`, `libraries` and `uses.never`; `xarch check` does not run the linter."

Check:
```bash
grep -n 'forbidden' README.md
```
Expected: nothing.

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, under `## [Unreleased]` / `### Changed`, after the bullet "The part key `tier` is renamed
`tests`: ...", add:

```markdown
- The part key `forbidden` is now `uses: {never: <list>}`, the top-level block `forbidden` is `never`, and a tier's
  `apply_forbidden: true` is `uses: {apply_never: true}`. The rule id is `never-use`, in findings, in JSON and under
  `hints`, and a finding's message ends with the new key, such as `(parts.domain.uses.never)`; `where` prints
  `never uses:` and its JSON field is `never_uses`; the `Loosened` keys are `uses.never` and `uses.apply_never`. Each
  old name is refused with its new form, which `xarch profile explain <old address>` also gives, and `never:` on a
  part or `apply_never:` on a tier is told it is a key of `uses`. Finding and fix texts are otherwise unchanged.
```

(A blank line separates it from the bullet before, as the others are.)

- [ ] **Step 3: The README test and the golden docs**

```bash
uv run pytest -q tests/architecture/test_readme.py tests/bootstrap/test_docs_templates.py 2>&1 | tail -3
uv run python -I /tmp/xarch-2-2/regenerate_docs.py "$PWD" && git diff --stat -- docs
```
Expected: PASS, and the regeneration moves nothing (`git diff --stat` empty).

- [ ] **Step 4: The gates, compared with the baseline**

```bash
uv run xarch check > /tmp/xarch-2-2/check-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/check-after.txt
uv run xarch check --strict > /tmp/xarch-2-2/strict-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/strict-after.txt
uv run xarch profile check architecture.yaml > /tmp/xarch-2-2/profile-check-after.txt 2>&1; echo "exit $?" >> /tmp/xarch-2-2/profile-check-after.txt
diff /tmp/xarch-2-2/check.txt /tmp/xarch-2-2/check-after.txt
diff /tmp/xarch-2-2/strict.txt /tmp/xarch-2-2/strict-after.txt
diff /tmp/xarch-2-2/profile-check.txt /tmp/xarch-2-2/profile-check-after.txt
uv run ruff check
timeout 1200 uv run pytest -q > /tmp/xarch-2-2/final-pytest.txt 2>&1 &
echo $! > /tmp/xarch-2-2/final-pytest.pid
```
Expected: the three runs end `exit 0` and every `diff` is empty; `ruff check` clean. When the PID has exited,
`tail -5 /tmp/xarch-2-2/final-pytest.txt`: all passed, more than the baseline count of Task 1 Step 1, with
`test_recorded_corpora.py`, `test_docs_templates.py`, `test_readme.py`, `test_key_catalogue.py` and
`test_needs_agree.py` among them.

Last greps:
```bash
grep -nw 'forbidden\|apply_forbidden' architecture.yaml xarch/architectures/cli.yaml xarch/architectures/web.yaml tests/bootstrap/corpora/stress.yaml tests/bootstrap/corpora/7cc6111.yaml tests/bootstrap/corpora/df537ca.yaml
grep -rn '`forbidden`\|`apply_forbidden`\|apply_forbidden\|parts\.[A-Za-z<>_.-]*\.forbidden' xarch README.md
git diff 1fcce88 --stat -- docs/examples xarch/architectures/examples tests/bootstrap/corpora/*.tar.xz
```
Expected: all three print nothing. (The second grep leaves out the Python attribute `where.forbidden`, which stays
until step 2.4; the third compares with `1fcce88`, the tip this branch is stacked on, because `main` lacks the earlier
steps' own edits of the archives.)

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git status --short
git commit -m "$(cat <<'EOF'
README names uses: {never} on a part, the block never and uses: {apply_never} on a tier, the rule never-use and its keys, the where field never_uses and the Loosened keys uses.never and uses.apply_never; the CHANGELOG says forbidden is now uses: {never: <list>}, every old name refused with its new form

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

`git status --short` before the commit shows only `README.md` and `CHANGELOG.md` staged (and the untracked spec and
plan under `docs/superpowers/`, which are not added).

---

## Self-review against the spec

- 1.1 (top-level `never`, its messages, entries at `never.<list>`): Task 1 Steps 2, 9, 13 (`test_bad_forbidden_lists_are_refused`, the name tests of `test_forbidden.py`, `test_architecture_files.py`).
- 1.2 (a part's `uses`, every message, `never` refused → no problem of its own, same `Architecture`): Task 1 Step 2
  (`test_a_part_s_uses_written_wrong_is_refused_at_its_address`, `..._the_file_does_not_hold_...`,
  `test_a_never_that_is_no_mapping_...`, `test_a_part_naming_a_list_under_uses_never_uses_...`) and Step 9; the
  recorded corpora and bundled-profile tests prove the same findings; the "a list may include others" clause is not
  written.
- 1.3 (a tier's `uses`, messages, `false` same as none): Task 1 Step 2 (the tier table, `test_apply_never_false_...`,
  `test_a_tier_may_hold_...`).
- 1.4 (key table, scopes, `NEEDS`, the needs check one level into the group): Task 1 Steps 3, 6, 7, 10; Task 2 Step 3
  for the rule ids; no row `forbidden`/`apply_forbidden` remains (Task 3's `test_no_entry_names_a_key_its_scope_still_has`
  and the table itself).
- 1.5 (rule id `never-use`, messages, `hints`, own ids, `--rule`, `KEYS`): Task 2.
- 1.6 (`profile explain` texts, `review.never` clause, no text naming `forbidden`): Task 1 Steps 4, 8; Task 4 Step 5
  for `alike`.
- 2.1 `where`: Task 4 Steps 1, 3. 2.2 `Loosened`: Task 4 Steps 1, 4 (unit and JSON). 2.3 `alike`: Task 4 Steps 1, 5.
  2.4 the variable `key`: Task 4 Step 6. 2.5 agents.md: Task 4 Step 6.
- 3.1-3.8 (the seven entries, the six refusals word for word, value never shown, sorted order with `tier`, file and
  parts together, `forbidden` beside `never`/`uses`, `hints.forbidden` with an own check, `profile explain` of each
  address): Task 3, and Task 2 Step 1 for 3.7. 3.9 (no `imports` entry): no task adds it.
- 4.1-4.3 (profiles, prose, grep): Task 1 Step 12, Task 5 Step 3, Task 6 Step 4. 4.4-4.5 (recordings by hand, the
  diff, the corpora test): Task 2 Steps 5-8. 4.6 (gates): Task 6 Step 4.
- 5.1-5.3 (rule line, template prose, enforcement paragraph, golden docs regenerated, diff read): Task 5.
- 6 (the "use" lists): Task 1 Step 13 and the constants of Task 3.
- 7.1 README: Task 2 Step 3 (the rule list) and Task 6 Step 1. 7.2 CHANGELOG: Task 6 Step 2.
- Spec tests 1-17: 1 Task 3 (`test_profile_keys.py`); 2 Task 3 (`test_retired_keys.py`); 3 Task 3
  (`test_forbidden.py`; `hints.forbidden` with an own check in Task 2's `test_written_checks.py`); 4 Task 1
  (`test_forbidden.py`); 5 Task 1 (`test_profile_needs.py`); 6 Task 2; 7 Task 2 (`test_violations.py`,
  `test_written_checks.py`, `test_rule_ids.py`); 8 Task 4 (`test_looseness.py`, `test_origin.py`); 9 Task 4
  (`test_evals.py`); 10 Task 4 (`tests/cli/reports/test_where_report.py`, `tests/bootstrap/test_where.py`); 11 Task 5;
  12 Task 1 and Task 3 (`test_explain.py`); 13 Task 1 and Task 3 (`test_profile_explain.py`); 14 Task 3
  (`test_architecture_files.py`); 15-17 Task 1 Step 13, Task 2 Step 1, and the suites of each task.
- Deviations from the spec's lists, with the reason:
  - The spec's test 10 names `test_where.py` of the rules logic: it asserts the contract field `forbidden`, a Python
    name that stays until step 2.4, so it is not edited; the `where` words are pinned by
    `tests/cli/reports/test_where_report.py` and `tests/bootstrap/test_where.py`.
  - The spec's test 11 names `test_docs_template.py`: the rule line of this check is pinned in
    `tests/modules/spec/application/logic/test_forbidden.py` and `tests/bootstrap/test_bundled_guards.py`, which Task
    5 edits; `test_docs_template.py` pins no line of it.
  - The spec's test 15 lists `tests/modules/rules/builders.py` among the fixtures writing `forbidden`: it builds
    domain values whose field `forbidden` is an internal name (step 2.4); only its docstring's key name changes (Task
    2).
  - The spec's 5.2 quotes "a tier no longer `uses.apply_never`"; the template's sentence is "a tier that lost a
    `types_only` part or its `apply_forbidden`", so Task 5 swaps the key in that sentence and keeps its words.
  - The parser tests sit in the existing `tests/modules/spec/application/logic/test_forbidden.py` (the spec lets the
    planner pick one home), its name kept as step 2.4 asks.
  - `expansion.KEYS` and the engine's `key=` strings move in Task 2, not Task 1, so the recordings are edited once;
    between the two commits `profile explain parts.uses.never --rule` says the key expands to no rule.
<!-- task-pipeline: validated -->
