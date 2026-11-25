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
