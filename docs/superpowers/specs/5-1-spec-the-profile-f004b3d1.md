# 5.1: the profile compared with is chosen by its structural match, printed on every run

Card `f004b3d1`, subtask of `3c8f968f`, release step 16 of the merged order (`0.3.0-cohesion-review-3.md`, section 3),
split with 5.2 to 5.4. Parent design: `/home/mtts/.claude/bedtime/xarch-2026-11-16-audits/profile-comparison-design.md`
(cited below as "note §n, line L"). This step builds note §2 (match and worked numbers), §3, §5 items 1, 2, 7, 10 (match
and pairing only), 12 (the match; `closest`), and the logic tests of §5.

## 1. What changes for a person

Today a custom profile is compared with its `based_on` bundled profile, else with the bundled profile sharing the most
part names, and nothing says how much the two profiles have in common. After this step:

1. Each comparison has a **match**: the share of what `check` reads under either profile that has a counterpart in the
   other (note §2, lines 145-177). It is printed on every run that compares, in text and in JSON (note, dodges, lines
   412-413), with counts by kind and the parts and tiers that have no counterpart.
2. A match below 75% is **low** and says so, with the reason (note §2, line 179; ruling line 30).
3. With no `based_on`, the profile is compared with the bundled profile of **highest match**, the lowest name on a tie;
   a bundled profile no part pairs with is no candidate (note §3, lines 236-238).
4. Parts are paired **by name, then by layout path**; tiers by name, then by subject (note §2, lines 167-171). The
   looser list compares paired parts and tiers, so a part renamed in place is still compared (note §5 item 1, lines
   322-325).
5. `check --format json` renames `enforcement.profile.closest` to `compared_with` (note §1, line 140; ruling line 37).

`based_on` naming a bundled profile still wins over a higher match (note §3, line 244). Nothing about `--strict`'s
verdicts changes: it reads `baseline_off` and the litmus of the profile compared with, exactly as today.

## 2. The items (normative)

Each profile is turned into a set of items, one per thing `check` reads (note §2, lines 151-162). Every item has a
**holder** and a **kind** (the kind is the bucket of the counts). Built on the 0.3.0 `Architecture` as parsed
(`xarch/modules/spec/domain/values.py:340-410`, `Part` at `:73-97`, `Tier` at `:195-233`, `Held` at
`xarch/modules/spec/domain/published.py:54-62`).

Kind `parts`, holder the part:
- one item per part (where its files sit).

Kind `part_keys`, holder the part, one item each when the part has it:
- `imports.may`: the part has a non-empty row in `rules`;
- `imports.libraries`: `imports_libraries` is not None and lists the part;
- `imports.must`: `Part.imports_must` is non-empty;
- `imports.may.types_only`: one item per target of `Part.imports_types_only` (addressed by the target, its part name
  read through the pairing);
- `uses.never`: `uses_never` lists the part;
- `holds.<kind>`: one item per kind of `Part.holds`; and one more per setting the kind writes: `names` non-empty,
  `immutable` true, `built_by` non-empty (each its own item; note §2, line 155, and the inferred shift at lines
  192-194);
- `untested` non-empty, `litmus` non-empty, `shared` not None, `entry` true;
- `package_only`: the part is listed by the `PackageOnly` guard (`parts.<part>.package_only` in the format).

`parts.<part>.tests` is not a separate item: the parser turns it into the tier's subject, counted once below as a
subject entry. `testing.beside` (note §2, line 160) does not exist as a key or field on this branch (no such key in
`xarch/architectures/presets/format/keys.yaml`, no field in `Framework`), so it is not an item. Its looser line is
5.2's work.

Kind `tiers`, holder the tier, or the tier and a part:
- one item per tier;
- one item per `Subject` of the tier, held by the tier **and** its part;
- one item per tier key with a value: `imports.types_only` non-empty, `uses.apply_never` true, `imports.also`
  non-empty, `imports.must` non-empty, `imports.may` **not None** (an empty tuple `()` is a value; `None` is no folder,
  no key; this settles the edge named at note line 431), `plain_tables` true.

Kind `guards`, holder the profile: one item per guard switched on (`KEY[type(guard)]`), `no-callbacks` among them. A
guard's parameters (its `parts`, `min_*`, `known`, `translated`) are not items.

Kind `profile`, holder the profile, one item each:
- `libraries`: `imports_libraries` is not None;
- `testing.skips`: `framework` is not None and its `skips` is non-empty (one item for the list);
- each `reserved` module; each `files` entry (by path); each `excluded` folder (by path); `fakes` not None;
- each check the profile writes itself (`checks.<id>`).

Left out (note §2, line 164): `review.*`, `evals.*`, `layers`, `docs`, `examples`, `hints`, `naming`, `notes`.

### Pairing

- Parts: each part of this profile pairs with the other profile's part of the same name; a part left unpaired then
  pairs with an unpaired part of the other that has the same `Part.path` (the tuple as written, `*` included), taking
  the other's parts in their order; each part pairs at most once.
- Tiers: by name; a tier left unpaired then pairs with an unpaired tier of the other whose subject, its parts read
  through the part pairing, is the same set of `(part, sub)`; at most once.
- An item is **comparable** when every holder it has is paired: a part key its part, a tier key its tier, a subject
  entry its tier and its part. Guards and profile keys sit in the profile, always paired. A check of the profile's own
  is comparable only when the other profile writes a check of the same id (note §2, lines 169-171).
- A key one profile writes and the other does not, on a paired holder, is comparable (note §2, lines 173-175).

### The number

    match = comparable items / all items

`all items` is the union of both profiles' items, a comparable item that both have counted once (addressed through the
pairing), each item that is not comparable counted on its side. Compared as an exact fraction. `low` is
`match < LOW`, `LOW = 0.75`, on the exact fraction: exactly 75% is not low (note §5 tests, line 372).

`counts`, in this order: `parts`, `part_keys`, `tiers`, `guards`, `profile`, each `(comparable, all)` for its kind; a
check of the profile's own counts under `profile`.

`only_here` / `only_there`: the parts, then the tiers, of this profile / of the other that are unpaired, each as
`"part <name>"` or `"tier <name>"`, by name within each.

`elsewhere`: each part paired by name whose path differs, as `"<name>: <the other's path joined with /> there"`, in
the order of this profile's parts. The note's dodge (lines 414-415, applying per the card) requires a pair by name at
another path to be named; this field carries it.

### Recomputed numbers (0.3.0 profiles on this branch)

Recomputed by a scratch sketch of the rules above (`/tmp/match51/match.py`, not xarch code) over
`load_architecture`. These are the numbers the built code must reproduce. The note's numbers (§2 table, lines 201-211)
are of the 0.2.0 profiles. Every difference is in `part_keys`, because a kind's settings now count one each, as the note
predicted at lines 192-194. The order of the rows holds.

| Profile | Against | Parts | Part keys | Tier entries | Guards | Profile keys | Match |
|---|---|---|---|---|---|---|---|
| `architecture.yaml` | cli | 12/15 | 72/91 | 21/31 | 11/11 | 9/9 | 125/157 = 79.6% |
| `architecture.yaml` | web | 11/16 | 67/96 | 21/31 | 11/11 | 9/9 | 119/163 = 73.0%, low |
| cli | web | 11/13 | 64/74 | 16/18 | 11/11 | 6/6 | 108/122 = 88.5% |
| `tests/bootstrap/corpora/stress.yaml` | cli | 11/14 | 75/93 | 19/30 | 11/11 | 10/10 | 126/158 = 79.7% |
| `tests/bootstrap/corpora/stress.yaml` | web | 10/15 | 70/97 | 19/30 | 11/11 | 10/10 | 120/163 = 73.6%, low |

`architecture.yaml` against cli: only here parts `main`, `profile-values`, `reports` and tier `wired`; only in cli tier
`rendering`; no part paired by name at another path. No pair in the repo pairs by path, so the `compared:` list of
`architecture.yaml` does not change.

**The gate's 81%.** The card's gate reads "match 81% with cli". 81% is the 0.2.0 number (note line 203). By the rules
above, on this branch's profiles, the run prints **80%** (125/157 rounded). The rules are not tuned to reach 81%
(note dodges, lines 408-410; card: "tuning the score until xarch's own profile reads high"). The gate is met when
`profile check architecture.yaml` prints `match: 80% with cli (based_on)` with the counts above and the same `compared:`
list as today. If the built code prints another number, the implementer reports it with each row of the table above
before and after. Adjusting an item rule until the number fits is not allowed.

## 3. Choosing the profile compared with

`origin_of(location, architecture, bundled, others)` (`xarch/modules/spec/application/logic/looseness.py:134`; every
`looseness.py` below is this file), `others` being the bundled profiles by
name (service unchanged: `services/architecture.py:114`):

- A bundled profile in force is its own baseline, as today: nothing compared, no match.
- `based_on` names a profile in `others`: that one, `chosen_by = "based_on"`, **even when no part pairs** (note §4,
  line 266). Then the match is low with the reason "no part in common".
- Else the profile of `others` with the highest match, the lowest name on a tie (exact fractions), `chosen_by =
  "closest"`. A profile no part pairs with is no candidate. None left: nothing compared, as today.
- `chosen_by = "against"` is reserved for 5.3. This step never produces it.
- With `chosen_by = "based_on"`, when another bundled profile has a strictly higher match, the origin names the
  highest of them (lowest name on a tie) and its match as `higher` (note §3, lines 244-246).

## 4. `Origin` and `Resemblance` (domain)

`xarch/modules/spec/domain/published.py:140-150` `Origin` (re-exported by the contract unchanged): `closest` becomes
`compared: str | None` (note §5 item 2, line 327), and it gains, all defaulted so a bundled or uncompared origin needs
none of them:

- `chosen_by: str | None = None`: `"based_on"` or `"closest"`; None when nothing is compared;
- `match: float | None = None`: the match rounded to two decimals; None when nothing is compared;
- `low: bool = False`;
- `counts: tuple[tuple[str, int, int], ...] = ()`: `(kind, comparable, all)` in the order of §2;
- `only_here: tuple[str, ...] = ()`, `only_there: tuple[str, ...] = ()`, `elsewhere: tuple[str, ...] = ()`;
- `higher: tuple[str, float] | None = None`: (name, match rounded to two decimals).

The field order stays positional-compatible with today's first six positions (`location, bundled, compared,
guards_off, baseline_off, looser`), with the new fields after them, so existing positional constructions keep working
once `closest` is renamed.

`xarch/modules/rules/domain/published.py:130-137` `Resemblance(bundled, closest, looser)` becomes `Resemblance(bundled,
compared, looser, chosen_by, match, low, counts, only_here, only_there, elsewhere, higher)`, the same defaults.
`rules/adapters/spec_profile.py:121-124` copies each field over. Docstrings of both say what each field is: "the
profile compared with", not "the closest bundled".

`LOW = 0.75` is a public constant of `looseness.py`.

## 5. `_looser` over the pairing (note §5 item 1, lines 322-325)

`_looser(custom, base)` compares each part of custom with the part of base it pairs with (not only same-name parts),
and each tier with the tier it pairs with. Before `_covers` compares a custom target with base's targets, the target's
part is translated to base's name through the pairing. Every other place that compares a part name across the two
(`imports.types_only` of a tier, `translated`, `evals.placement.lines`) goes through the pairing the same way. Sentences
keep naming custom's part and tier names. With every pair by name (all profiles in the repo), the output is unchanged.
The module docstring (`looseness.py:1-23`) is rewritten to say: compared with based_on, else the highest match; the
items and pairing; looser compared only on paired parts and tiers.

## 6. Output

### `xarch profile check` text (`cli/reports/profile_report.py`)

Header (`origin_words`, `:185-191`):
- bundled: `bundled` (unchanged);
- `chosen_by = "based_on"`: `custom; based_on: cli`;
- `chosen_by = "closest"`: `custom; closest bundled: cli, match 80%`;
- nothing compared: `custom; no bundled profile resembles it` (unchanged).

Match lines, printed whenever something is compared, just before `compared:`:

    checking architecture.yaml (custom; based_on: cli)
      loads: ok
      files: all 23 it points to are present
      examples: ok: they import only what their part may
      match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them
        only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering
      compared: looser than cli (information; ...):
        ...(the 18 lines of today, unchanged)
    OK: the profile is valid

- The percentage is the match times 100, rounded to a whole number (`80%`).
- `only here: <parts>; <tiers>. only in <name>: <parts>; <tiers>`. Each group is `part x`/`parts x, y`, `tier x`/`tiers
  x, y`, up to five names and then `and N more`. An empty group is left out, an empty side is left out, and when both
  sides are empty the line is left out.
- When `elsewhere` is not empty: `    same name, other path: domain: modules/*/domain there, ...`, five and `and N more`.
- Low: one more line, `    low: 27% of what check reads under either profile has nothing to compare with in the
  other, so the list below says little about how check would do under web`. The 27% is 100 minus the printed match.
  When no part pairs: `    low: no part in common, so the list below says little about how check would do under
  web`.
- `higher`: one more line, `    web matches 88%`.

### `xarch check` text, enforcement section (`cli/reports/report.py:79-82`)

    enforcement
      profile:     architecture.yaml (custom; compared with cli, based_on; match 80%)

`(custom; compared with <name>, <chosen_by>; match <n>%)`. A bundled profile reads `(bundled)` and an uncompared one
`(custom; no bundled profile resembles it)`, as today. When low, one line under it at indent 4, labelled `match`:
`match:  73%, low: <the same reason as profile check>` (note §1, line 135). The match is not hidden when it is not
low: it sits in the profile line.

### JSON

`profile check --format json` (`check_document`, `:246-259`): `compared_with` stays null when nothing is compared,
else `{"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there", "elsewhere", "higher", "looser"}`,
with `counts` `{"parts": [12, 15], "part_keys": [72, 91], "tiers": [21, 31], "guards": [11, 11], "profile": [9, 9]}`,
`match` the two-decimal number (`0.8`), and `higher` null or `{"profile", "match"}` (note §1, lines 137-139).

`check --format json` (`_enforcement_document`, `report.py:142-145`): `enforcement.profile.closest` is gone, and
`enforcement.profile.compared_with` takes its place with the same object as `profile check`'s, built by one shared
function (null when nothing is compared). `enforcement.profile.looser`, `guards_off` and `baseline_off` stay where
they are. No `closest` key remains anywhere in either document (note dodges, line 426).

## 7. Docs

- README (note §5 item 10): the `profile` bullet of the enforcement section (`README.md:436-447`): compared with
  `based_on` if given, else the bundled profile of highest match; the match, its counts and "low" below 75%; pairing by
  name, then path; the looser ways compared on paired parts and tiers. The sample at `:420` reads `(custom; compared
  with web, closest; match NN%)`. The JSON sample at `:361` reads `"compared_with": null`. The `profile check`
  paragraph (`:235-242`) names the match line and the new `compared_with` fields. `--against` is not mentioned
  (5.3).
- CHANGELOG `[Unreleased]` (review 3, O4, O5; note §5 item 12): under Added, the match (what it counts, 75% low,
  printed on every run that compares, `compared_with`'s new fields); under Changed, without `based_on` the closest
  bundled profile is the one of highest match, parts paired by name then path, and `check`'s JSON key
  `enforcement.profile.closest` is now `compared_with`.
- Help and docstrings that this step's fields make false (`enforcement.py:21`, `profile_report.py:193`, the
  `Origin`/`Resemblance` docstrings) say "the profile it is compared with". The wider wording sweep of note §5 item 8
  belongs to 5.3.
- Golden docs `docs/{cli,web,xarch}/testing.md`: regenerated with the suite's own generation and the diff read. This
  step changes no profile and no template, so the expected diff is empty (O8). Never edited by hand.

## 8. Error paths and edges

- A profile whose `based_on` names a bundled profile it shares no part with: compared with it, `low`, reason "no part
  in common", `only_here` lists all its parts, the looser list holds only what profile-wide keys and guards give.
- A custom profile no bundled profile pairs a part with, and no `based_on`: no comparison, header `no bundled profile
  resembles it`, no match line, `compared_with: null` in both JSON documents; `--strict` excuses no guard (today's
  rule).
- A tie on the exact match between two bundled profiles: the lower name.
- Two parts of the other profile with the same path as one unpaired part: the first in the other's order pairs;
  each pairs at most once.
- A tier with `imports.may` of `()` against one of `None`: an item on the first side only (comparable when the tiers
  pair).
- `_sentence` raises for an unknown key, as today; no new key is added to `LOOSER` here (5.2).

## 9. Tests (written first)

Logic tier (`tests/modules/spec/application/logic/test_looseness.py`): the rules are pure functions over hand-built
`Architecture`s (`tests/modules/spec/profiles.py` `layered`/`parsed`, `tests/modules/spec/application/origins.py`), so
the match and pairing are proved there without files (note §5 tests, lines 368-372):

1. `test_a_copy_of_a_profile_matches_it_at_100_percent`: `origin_of` of `parsed(layered())` against itself:
   `match == 1.0`, not low, `only_here == only_there == ()`.
2. `test_a_part_renamed_in_place_pairs_by_its_path_and_is_compared_under_its_own_name`: rename `api` to `routes`
   keeping its path; add a target to its `imports.may`: matched, and the looser line names `routes`.
3. `test_a_target_naming_a_part_renamed_in_place_is_read_through_the_pairing`: custom's `service` may import `routes`
   (the renamed `api`) where base's may import `api`: not looser.
4. `test_a_tier_renamed_with_the_same_subject_pairs_by_subject`: a tier renamed with its subject kept: its items are
   comparable, and a dropped `uses.apply_never` is listed under the new name.
5. `test_a_key_one_side_drops_on_a_paired_part_is_comparable_and_listed_looser`: drop a `litmus` from a paired part:
   the match stays 100% and the litmus line is listed.
6. `test_the_items_of_an_unpaired_part_are_not_comparable`: a part of custom's own with N keys: the `parts` and
   `part_keys` counts show it, and `only_here == ("part <name>",)`.
7. `test_guards_and_profile_keys_are_always_comparable`: guards on one side only and a `reserved` module on one side
   only: the `guards` and `profile` counts are `(n, n)`.
8. `test_each_setting_of_a_held_kind_is_an_item_of_its_own`: `holds: {classes: {names, immutable, built_by}}` gives
   four `part_keys` items.
9. `test_a_tier_folder_written_empty_is_an_item_and_no_folder_is_none`: the `imports.may` `()` versus `None` edge.
10. `test_a_check_of_the_profile_s_own_is_comparable_only_with_the_same_id`.
11. `test_a_bundled_profile_no_part_pairs_with_is_no_candidate`: `others` sharing no part and no `based_on`: nothing is
    compared (`compared is None`, `match is None`).
12. `test_the_bundled_profile_of_highest_match_is_compared_the_lowest_name_on_a_tie`: three bundled profiles, one
    clearly higher; then two equal: the lower name. Replaces the "most parts" choice.
13. `test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_of_highest_match` (renamed from
    `..._wins_over_the_one_sharing_most_parts`, note line 382): `chosen_by == "based_on"`, and `higher` names the better one.
14. `test_based_on_a_bundled_profile_sharing_no_part_is_compared_low_with_no_part_in_common`.
15. `test_a_match_of_exactly_75_percent_is_not_low_and_just_below_is`: two profiles built so comparable/all is exactly
    3/4 (`low` False, `match == 0.75`), then one more item on an unpaired part so it falls just below (`low` True).
    Also asserts `LOW == 0.75`.
16. `test_the_counts_are_by_kind_in_order`: `[k for k, _, _ in counts] == ["parts", "part_keys", "tiers", "guards",
    "profile"]`.
17. `test_a_pair_by_name_at_another_path_is_named_elsewhere`.

Service tier (`tests/modules/spec/application/test_origin.py`): the use case through the controller with fake files;
edited for the rename and new fields: `closest` → `compared`; the "sharing the most parts" test becomes "the highest
match, the first by name on a tie"; the bundled case stays `Origin("base", True, None, OFF, OFF, ())`. The copy case
also asserts `chosen_by == "closest"` and `match == 1.0`.

Report tier (`tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py`): formatting of hand-made
`Origin`/`Resemblance` values, no profile loaded:
- the header for based_on, closest (with match), none;
- the match line, the `only` line with five names and `and N more`, the empty-side and both-empty cases, the low line
  with the percentage reason and with "no part in common", the `higher` line, the `same name, other path` line;
- the enforcement profile line `(custom; compared with web, closest; match 81%)` and the `match:` low line under it;
- both JSON documents: `compared_with` with every field, null when nothing is compared, and no `closest` key in
  `check`'s document.

Bootstrap tier (`tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_enforcement.py`): the real
profiles through the wired app, because the gate's number belongs to the shipped profiles:
- `profile check architecture.yaml` prints `checking architecture.yaml (custom; based_on: cli)` and `match: 80% with
  cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit
  where both profiles have them` and the `only here` line of §6 (the existing `custom; closest bundled: web` assertion
  at `test_profile_check.py:42` moves to the new header words);
- its JSON `compared_with` holds `chosen_by: "based_on"`, `match: 0.8`, `low: false`, the counts of §2;
- `check`'s JSON on a custom profile has `enforcement.profile.compared_with` and no `closest`; its text enforcement line
  reads `compared with ..., ...; match N%`;
- the six `closest` lines of `test_check_enforcement.py` follow the new key.

Edited elsewhere for the rename only: `tests/modules/rules/application/logic/test_enforcement.py`,
`tests/modules/spec/application/test_profile_loading.py`, and every `Origin(`/`Resemblance(` construction (they keep
working positionally; any keyword `closest=` becomes `compared=`). `tests/bootstrap/test_recorded_corpora.py` and
`tests/bootstrap/corpora/` do not move.

## 10. Gates

On this branch alone, the full suite green: `uv run ruff check` (never `--fix`), `uv run xarch check`, `uv run xarch
check --strict`, `uv run xarch profile check architecture.yaml` (prints the match line of §6, 80% by §2's recompute,
and the same 18 `compared:` lines as before), and `uv run pytest -q` in the background with `timeout`.

## 11. Project rules that bind the work

No comments in xarch's code (docstrings are fine); never `ruff --fix`; tests first; examples simple, absolute `app.`
imports; `from __future__ import annotations` in `looseness.py`; Python only in the reader adapter and the data files
under `xarch/architectures/presets/`; recorded corpora not edited; README and CHANGELOG lines under `[Unreleased]`;
golden docs regenerated, never edited by hand; `.claude/` stays out of commits; nothing pushed.

## 12. Out of scope

- `--against`, `chosen_by = "against"`, the refusal of `--strict --against`, the bundled-in-force comparison, the
  wording sweep of note §5 item 8, and README's `--against` lines: **5.3**.
- `based_on` as a path, the chain, `anchor`, the 4.1 `--strict` rule: **5.4**.
- New looser lines (`holds`, settings, `shared`, `imports.may.types_only` widening, tier `imports.must`,
  `plain_tables`, `testing.beside`) and the item for `testing.beside`: **5.2**.
- The other-language reason (note line 186-188): no second language exists.
- Pairing by role, by row, or by tier membership, which the note sets aside (dodges, lines 416-417).
- Any change of `LOW`, of an item rule, or of the rounding to make a repo profile read high or not low.

## For the planner

Plan per `writing-plans`: one task per deliverable with its own red/green cycle. A natural order: (1) items, pairing,
match, `LOW` in `looseness.py` with logic tests 1-10, 15-17; (2) `Origin` fields and the `closest` → `compared` rename
through spec, rules `Resemblance`, the adapter, with `_closest` by match (tests 11-14, service tests); (3) `_looser`
over the pairing (tests 2-4); (4) `profile check` text and JSON (report tests); (5) `check` enforcement text and JSON
(report tests); (6) bootstrap tests, README, CHANGELOG, golden-doc regeneration, gates. Review Focus candidates: a
profile whose `based_on` shares no part; a tie on the exact fraction; a renamed part whose targets are named by the
other's name; percentages that round to 75% while below it (74.6% prints `75%` but is low; the low line must still
show); an empty `only` side.
