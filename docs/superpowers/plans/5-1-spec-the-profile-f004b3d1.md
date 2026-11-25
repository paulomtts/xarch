# 5.1 The profile compared with is chosen by its structural match, printed on every run — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every comparison of a custom profile with a bundled one a **match** (the share of what `check` reads
under either profile that has a counterpart in the other), choose the bundled profile by highest match when there is
no `based_on`, pair parts by name then layout path (tiers by name then subject), compare the looser list over that
pairing, and print the match in `profile check` and `check`, text and JSON, where `enforcement.profile.closest`
becomes `compared_with`.

**Architecture:** All the rules are pure functions in `xarch/modules/spec/application/logic/looseness.py`: items per
profile, the pairing, the counts by kind, the exact-fraction match, the choice of profile, and `_looser` reading every
cross-profile name through the pairing. `Origin` (spec, re-exported by its contract) and `Resemblance` (rules) gain
the same new fields, and the rules adapter copies them over. The two reports read them: `profile_report.py` owns the
words and the one JSON object (`compared_document`), which `report.py` reuses for `check`.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `ruff`, `fractions.Fraction`, xarch's own `xarch check` /
`xarch profile check`.

**Spec:** `docs/superpowers/specs/5-1-spec-the-profile-f004b3d1.md` (prepended below, verbatim).

Every number this plan asserts was reproduced by running the code of this plan on a scratch copy of the branch: the
five rows of the spec's §2 table, the gate's `match: 80% with cli (based_on): ...` line, every test below green, the
golden docs regenerating with an empty diff, `xarch check` and `xarch check --strict` exiting 0, and `_looser`'s
output on `architecture.yaml`, `tests/bootstrap/corpora/stress.yaml`, `cli` and `web` (each against `cli` and `web`)
byte-identical to today's.

## Global Constraints

- `LOW = 0.75`, a public constant of `looseness.py`; `low` is `match < LOW` on the **exact** fraction (exactly 75% is
  not low), or no part pairs.
- `Origin`'s first six positions stay `location, bundled, compared, guards_off, baseline_off, looser`; the new fields
  come after, all defaulted: `chosen_by: str | None = None`, `match: float | None = None`, `low: bool = False`,
  `counts: tuple[tuple[str, int, int], ...] = ()`, `only_here: tuple[str, ...] = ()`, `only_there: tuple[str, ...] =
  ()`, `elsewhere: tuple[str, ...] = ()`, `higher: tuple[str, float] | None = None`. `Resemblance(bundled, compared,
  looser, chosen_by, match, low, counts, only_here, only_there, elsewhere, higher)`, the same defaults.
- `chosen_by` is `"based_on"` or `"closest"` (never `"against"`: that is 5.3).
- `match` is the exact match rounded to two decimals (`round(float(fraction), 2)`); the printed percentage is
  `round(match * 100)`.
- `counts` order: `parts`, `part_keys`, `tiers`, `guards`, `profile`; a check of the profile's own counts under
  `profile`.
- With every pair by name (every profile in the repo), the looser list and its sentences are unchanged.
- No `closest` key remains in either JSON document.
- No comments in xarch's code (docstrings are fine); never `ruff --fix`; tests first; `from __future__ import
  annotations` stays in `looseness.py`; recorded corpora (`tests/bootstrap/corpora/`, `tests/bootstrap/test_recorded_corpora.py`)
  are not edited; README and CHANGELOG lines under `[Unreleased]`; golden docs `docs/{cli,web,xarch}/` regenerated,
  never edited by hand; `.claude/` stays out of commits; nothing pushed.
- Never tune `LOW`, an item rule or the rounding to make a repo profile read high or not low. If the gate prints a
  number other than 80%, report it with each row of the spec's §2 table before and after; do not adjust a rule.
- Run the full suite only in the background with `timeout` (it takes about four minutes):
  `timeout 900 uv run pytest -q -p no:cacheprovider`.

## Review Focus

1. A profile whose `based_on` names a bundled profile it shares no part with: it is still compared, `low` is true
   and the low line reads `no part in common`, not a percentage (logic test
   `test_based_on_a_bundled_profile_sharing_no_part_is_compared_low_with_no_part_in_common`, Task 2; report param
   `with no part in common`, Task 4).
2. A tie on the exact fraction between two bundled profiles: the lower name, for the profile chosen and for `higher`
   (`test_the_bundled_profile_of_highest_match_is_compared_the_lowest_name_on_a_tie`, Task 2; the service tie with
   `zeta`/`alpha`, Task 2).
3. A part renamed in place whose targets the other profile names by the old name: read through the pairing, so not
   listed looser (`test_a_target_naming_a_part_renamed_in_place_is_read_through_the_pairing`, Task 3).
4. A match below 75% that rounds to it (50/67 = 74.6% prints `75%`): still low, and the low line still shows, with
   `25%` (`test_a_match_that_rounds_to_75_percent_from_below_is_still_low`, Task 2; report param `a match just below
   75% that rounds to it is still low`, Task 4).
5. An empty `only` side, an empty group, both sides empty: the side, the group, or the whole line is left out, never
   an `only here: ` with nothing after it (`test_what_pairs_with_nothing_is_said_by_side_and_by_group`, Task 4).

---

## The spec

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

---

## File structure

- `xarch/modules/spec/domain/published.py` — `Origin` gains the comparison's fields, `closest` becomes `compared`;
  `BASED_ON`, `CLOSEST` (why a profile is compared with the one it is). Task 1.
- `xarch/modules/spec/contract/__init__.py` — re-exports `CLOSEST` for the command line. Task 1.
- `xarch/modules/rules/domain/published.py` — `Resemblance` gains the same fields. Task 1.
- `xarch/modules/rules/adapters/spec_profile.py` — copies every field of `Origin` into `Resemblance`. Task 1.
- `xarch/modules/rules/application/logic/enforcement.py` — one docstring phrase. Task 1.
- `xarch/modules/spec/application/logic/looseness.py` — items, pairing, counts, match, the choice (Task 2); `_looser`
  over the pairing and the module docstring (Task 3).
- `xarch/cli/reports/profile_report.py` — the header, the match lines, the low reason, `compared_document`. Task 4.
- `xarch/cli/reports/report.py` — the enforcement `profile:` line, its `match:` low line, `compared_with` in JSON.
  Task 4.
- `README.md`, `CHANGELOG.md` — Task 5. `docs/{cli,web,xarch}/` regenerated, expected unchanged — Task 5.
- Tests: `tests/modules/spec/application/logic/test_looseness.py` (Tasks 1-3),
  `tests/modules/spec/application/test_origin.py`, `tests/modules/spec/application/test_profile_loading.py`,
  `tests/modules/spec/application/test_check.py` (Tasks 1-2), `tests/modules/rules/adapters/test_spec_profile.py`,
  `tests/modules/rules/application/logic/test_enforcement.py` (Task 1), `tests/cli/reports/test_profile_report.py`,
  `tests/cli/reports/test_report.py`, `tests/bootstrap/test_profile_check.py`,
  `tests/bootstrap/test_check_enforcement.py` (Task 4).

---

### Task 1: `Origin` and `Resemblance` carry the comparison; `closest` becomes `compared`

Nothing a user sees changes in this task: the fields are added and defaulted, the attribute is renamed, and every
reader follows. The JSON key `closest` is still written (from `origin.compared`) until Task 4 replaces it.

**Files:**
- Modify: `xarch/modules/spec/domain/published.py:1-25` (module docstring, the `Origin`/`Loosened` lines) and
  `:139-150` (`Origin`)
- Modify: `xarch/modules/spec/contract/__init__.py:11-28` (import), `:38-48` (`__all__`)
- Modify: `xarch/modules/rules/domain/published.py:14-16` (module docstring) and `:130-137` (`Resemblance`)
- Modify: `xarch/modules/rules/adapters/spec_profile.py:121-124`
- Modify: `xarch/cli/reports/profile_report.py:185-191`, `:236-241`, `:253-258` (reads `.closest`)
- Modify: `xarch/cli/reports/report.py:145`
- Modify: `xarch/modules/rules/application/logic/enforcement.py:21`
- Test: `tests/modules/rules/adapters/test_spec_profile.py:68`, `:173-176`
- Test (rename only): `tests/modules/spec/application/logic/test_looseness.py:52-53`,
  `tests/modules/spec/application/test_origin.py:33,48,81,88-91`,
  `tests/modules/spec/application/test_profile_loading.py:47,52,58`,
  `tests/modules/rules/application/logic/test_enforcement.py:137`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Origin(location, bundled, compared, guards_off, baseline_off, looser, chosen_by, match, low, counts,
  only_here, only_there, elsewhere, higher)` (spec, `xarch.modules.spec.contract.Origin`);
  `BASED_ON = "based_on"`, `CLOSEST = "closest"` in `xarch.modules.spec.domain.published`, `CLOSEST` re-exported by
  `xarch.modules.spec.contract`; `Resemblance(bundled, compared, looser, chosen_by, match, low, counts, only_here,
  only_there, elsewhere, higher)` (rules, `xarch.modules.rules.contract.Resemblance`).

- [ ] **Step 1: Record what `profile check` prints today**

Run: `uv run xarch profile check architecture.yaml > /tmp/5-1-profile-check-before.txt; wc -l < /tmp/5-1-profile-check-before.txt`
Expected: `24` (header, loads, files, examples, `compared:`, 18 sentences, `OK: the profile is valid`). Task 5 diffs the
comparison against it.

- [ ] **Step 2: Write the failing test: the adapter copies every field**

In `tests/modules/rules/adapters/test_spec_profile.py`, replace line 68:

```python
ORIGIN = Origin("mine.yaml", False, "cli", ("closed-tree",), (), (Loosened("untested", "api"),))
```

with:

```python
COUNTS = (("parts", 3, 4), ("part_keys", 5, 6), ("tiers", 2, 2), ("guards", 1, 1), ("profile", 2, 2))
ORIGIN = Origin("mine.yaml", False, "cli", ("closed-tree",), (), (Loosened("untested", "api"),), "based_on", 0.87,
                False, COUNTS, ("part jobs",), ("tier rendering",), ("store: src/*/store there",), ("web", 0.9))
```

and in the parametrize of `test_spec_s_check_of_a_profile_that_loads_is_what_rules_reviews` (lines 173-176) replace:

```python
                          Resemblance(False, "cli", (published.Loosened("untested", "api"),))),
                 id="a profile that loads keeps its example problems, its files and how it resembles the bundled ones"),
```

with:

```python
                          Resemblance(False, "cli", (published.Loosened("untested", "api"),), "based_on", 0.87, False,
                                      COUNTS, ("part jobs",), ("tier rendering",), ("store: src/*/store there",),
                                      ("web", 0.9))),
                 id="a profile that loads keeps its example problems, its files and every field of how it resembles "
                    "the bundled ones"),
```

- [ ] **Step 3: Run it to see it fail**

Run: `timeout 120 uv run pytest -q tests/modules/rules/adapters/test_spec_profile.py`
Expected: collection ERROR, `TypeError: Origin.__init__() takes from 1 to 7 positional arguments but 15 were given`.

- [ ] **Step 4: Give `Origin` its fields, and name why it is compared**

In `xarch/modules/spec/domain/published.py`, in the module docstring replace:

```
    Origin       where the profile in force comes from and how far it can be trusted, which the command line shows
                 and the checking module reads the guards of
    Loosened     one way a profile is looser than the bundled one it resembles, held by Origin and shown as it is
```

with:

```
    Origin       where the profile in force comes from, the bundled profile it is compared with and how much the
                 two have in common, which the command line shows and the checking module reads the guards of;
                 BASED_ON and CLOSEST why it is compared with that one
    Loosened     one way a profile is looser than the bundled one it is compared with, held by Origin and shown as it
                 is
```

and replace the whole `Origin` class (from `@dataclass(frozen=True)` above `class Origin:` down to
`    looser: tuple[Loosened, ...] = ()`) with:

```python
BASED_ON, CLOSEST = "based_on", "closest"
"""Why a custom profile is compared with the bundled one it is (Origin.chosen_by): it says it is based on it, or that
one has the highest match."""


@dataclass(frozen=True)
class Origin:
    """Where a profile comes from and the profile it is compared with.

    location: as selected, a bundled name or a path
    bundled: whether it is a bundled profile, its own baseline
    compared: for a custom file, the bundled profile it is compared with; None when it is bundled or none is
    guards_off: the guards xarch has that it leaves off, in xarch's order
    baseline_off: those the bundled profile it is, or is compared with, leaves off too
    looser: how it is looser than the profile it is compared with
    chosen_by: why that one: BASED_ON or CLOSEST; None when nothing is compared
    match: the share of what `check` reads under either profile that has a counterpart in the other, rounded to two
        decimals; None when nothing is compared
    low: the match is below the line of a low one, or no part pairs
    counts: (kind, comparable, all) for each kind of thing `check` reads, in the order they are said
    only_here, only_there: the parts, then the tiers, of this profile, and of the one it is compared with, that pair
        with none of the other's, each as "part <name>" or "tier <name>", by name
    elsewhere: each part the other profile has by the same name at another path, as "<name>: <its path there> there"
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    """
    location: str = ""
    bundled: bool = True
    compared: str | None = None
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    looser: tuple[Loosened, ...] = ()
    chosen_by: str | None = None
    match: float | None = None
    low: bool = False
    counts: tuple[tuple[str, int, int], ...] = ()
    only_here: tuple[str, ...] = ()
    only_there: tuple[str, ...] = ()
    elsewhere: tuple[str, ...] = ()
    higher: tuple[str, float] | None = None
```

- [ ] **Step 5: Re-export `CLOSEST` from spec's contract**

In `xarch/modules/spec/contract/__init__.py`, in the import from `xarch.modules.spec.domain.published`, replace:

```python
from xarch.modules.spec.domain.published import (
    CHOICE,
```

with:

```python
from xarch.modules.spec.domain.published import (
    CHOICE,
    CLOSEST,
```

and in `__all__` replace `"NoProfileChosen", "SelectResult", "Origin", "Loosened", "LITMUS",` with
`"NoProfileChosen", "SelectResult", "Origin", "Loosened", "LITMUS", "CLOSEST",`.

- [ ] **Step 6: Give `Resemblance` the same fields**

In `xarch/modules/rules/domain/published.py`, in the module docstring replace:

```
    Loosened one way a profile is looser than the bundled one it resembles, which the command line shows
    Resemblance whether a profile is bundled, the bundled one it resembles and how it is looser, which the command
          line shows
```

with:

```
    Loosened one way a profile is looser than the bundled one it is compared with, which the command line shows
    Resemblance whether a profile is bundled, the bundled one it is compared with, how much the two have in common
          and how it is looser, which the command line shows
```

and replace the whole `Resemblance` class (from its `@dataclass(frozen=True)` down to
`    looser: tuple[Loosened, ...] = ()`) with:

```python
@dataclass(frozen=True)
class Resemblance:
    """How a profile stands to the bundled ones, as the spec module's origin of it says.

    bundled: whether it is one, its own baseline
    compared: the bundled profile it is compared with; None when it is bundled or none is
    looser: how it is looser than the profile it is compared with, in the order the spec module finds it
    chosen_by: why that one: "based_on", the profile says it is based on it, or "closest", it has the highest match;
        None when nothing is compared
    match: the share of what `check` reads under either profile that has a counterpart in the other, rounded to two
        decimals; None when nothing is compared
    low: the match is below the line of a low one, or no part pairs
    counts: (kind, comparable, all) for each kind of thing `check` reads, in the order they are said
    only_here, only_there: the parts, then the tiers, of this profile, and of the one it is compared with, that pair
        with none of the other's, each as "part <name>" or "tier <name>", by name
    elsewhere: each part the other profile has by the same name at another path, as "<name>: <its path there> there"
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    """
    bundled: bool
    compared: str | None = None
    looser: tuple[Loosened, ...] = ()
    chosen_by: str | None = None
    match: float | None = None
    low: bool = False
    counts: tuple[tuple[str, int, int], ...] = ()
    only_here: tuple[str, ...] = ()
    only_there: tuple[str, ...] = ()
    elsewhere: tuple[str, ...] = ()
    higher: tuple[str, float] | None = None
```

- [ ] **Step 7: The adapter copies every field**

In `xarch/modules/rules/adapters/spec_profile.py`, in `reviewed`, replace:

```python
                                Resemblance(origin.bundled, origin.closest, looser))
```

with:

```python
                                Resemblance(origin.bundled, origin.compared, looser, origin.chosen_by, origin.match,
                                            origin.low, origin.counts, origin.only_here, origin.only_there,
                                            origin.elsewhere, origin.higher))
```

- [ ] **Step 8: Every reader of `closest` reads `compared`**

In `xarch/cli/reports/profile_report.py`, replace every `.closest` with `.compared` (seven places: `origin_words`
lines 189-190, `_compared` lines 237, 240, 241, `check_document` lines 255-256), and in `xarch/cli/reports/report.py`
line 145 replace `"closest": origin.closest,` with `"closest": origin.compared,` (the key itself changes in Task 4).
In `xarch/modules/rules/application/logic/enforcement.py` line 21 replace
`Every other way a custom profile differs from the closest bundled one (`origin.looser`) is` with
`Every other way a custom profile differs from the profile it is compared with (`origin.looser`) is`.

Then in the tests, rename the attribute and the one test name:

```bash
sed -i 's/\.closest\b/.compared/g' tests/modules/spec/application/logic/test_looseness.py \
  tests/modules/spec/application/test_origin.py tests/modules/spec/application/test_profile_loading.py
sed -i 's/def test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_never_a_strict_finding/def test_how_a_custom_profile_differs_from_the_profile_it_is_compared_with_is_never_a_strict_finding/' \
  tests/modules/rules/application/logic/test_enforcement.py
grep -rn "closest" xarch --include=*.py
```

Expected from the grep, and nothing else: `report.py` (`"closest": origin.compared,`); in `looseness.py` the module
docstring's `The closest bundled profile`, `def _closest(`, `origin_of`'s docstring `the closest of the others` and
`name = _closest(architecture, others)` (Task 2 and Task 3 replace them); spec's `published.py`
`BASED_ON, CLOSEST = "based_on", "closest"`; rules' `published.py` `Resemblance` docstring (`or "closest", it has
the highest match`); and the unrelated `explained.py:94`, `explain.py:134`, `stand_ins.py:41` (nearest keys and
fakes, not profiles).

- [ ] **Step 9: Run the tests to see them pass**

Run: `timeout 600 uv run pytest -q tests/modules/rules tests/modules/spec tests/cli`
Expected: all pass.

Run: `uv run ruff check && uv run xarch check >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 10: Commit**

```bash
git add xarch/modules/spec/domain/published.py xarch/modules/spec/contract/__init__.py \
  xarch/modules/rules/domain/published.py xarch/modules/rules/adapters/spec_profile.py \
  xarch/modules/rules/application/logic/enforcement.py xarch/cli/reports/profile_report.py xarch/cli/reports/report.py \
  tests/modules/rules/adapters/test_spec_profile.py tests/modules/spec/application/logic/test_looseness.py \
  tests/modules/spec/application/test_origin.py tests/modules/spec/application/test_profile_loading.py \
  tests/modules/rules/application/logic/test_enforcement.py
git commit -m "Origin and Resemblance carry the comparison's fields, chosen_by, match, low, counts, only_here, only_there, elsewhere and higher, all defaulted, and closest becomes compared; the rules adapter copies every field; nothing a user sees changes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The match: items, pairing, counts, and the bundled profile of highest match

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (imports `:24-32`, constants after `LOOSER`, `_closest`
  `:49-55` replaced, `origin_of` `:134-148`)
- Test: `tests/modules/spec/application/logic/test_looseness.py`
- Test: `tests/modules/spec/application/test_origin.py`, `tests/modules/spec/application/test_profile_loading.py`,
  `tests/modules/spec/application/test_check.py`

**Interfaces:**
- Consumes: `Origin(..., chosen_by=, match=, low=, counts=, only_here=, only_there=, elsewhere=, higher=)`,
  `BASED_ON`, `CLOSEST` (Task 1).
- Produces (all in `looseness.py`): `LOW = 0.75`; `COUNTED = ("parts", "part_keys", "tiers", "guards", "profile")`;
  `_paired_parts(mine: Architecture, other: Architecture) -> dict[str, str]` (mine's name → other's name);
  `_paired_tiers(mine: Architecture, other: Architecture, parts: Mapping[str, str]) -> dict[str, str]`;
  `_into(target: Target, parts: Mapping[str, str]) -> Target` (a target with its part renamed through parts);
  `_counts(mine, other) -> tuple[tuple[str, int, int], ...]`; `_share(counts) -> Fraction`. Task 3 uses
  `_paired_parts`, `_paired_tiers` and `_into`.

- [ ] **Step 1: Write the failing logic tests**

In `tests/modules/spec/application/logic/test_looseness.py`:

Replace the two import lines

```python
from xarch.modules.spec.application.logic.looseness import LOOSER, origin_of
from xarch.modules.spec.domain.published import Loosened
```

with:

```python
from xarch.modules.spec.application.logic.looseness import LOOSER, LOW, origin_of
from xarch.modules.spec.domain.published import Loosened, Origin
```

Delete the whole test `test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_sharing_most_parts`
(lines 48-53; after Task 1 it reads `.compared`): the new test 13 below replaces it.

Append at the end of the file:

```python
def bare(**paths: str) -> Architecture:
    """A profile of the parts given, each at its path, checking no outside package: one item per part and no more."""
    return replace(parsed({"name": "bare", "parts": {name: {"path": path, "role": "code"} for name, path in paths.items()}}),
                   imports_libraries=None)


def compared(custom: Architecture, base: Architecture) -> Origin:
    """The origin of custom, based on base."""
    return origin_of("mine.yaml", replace(custom, based_on="base"), False, {"base": base})


def test_a_copy_of_a_profile_matches_it_at_100_percent():
    origin = origin_of("mine.yaml", parsed(layered()), False, {"base": parsed(layered())})
    assert (origin.compared, origin.chosen_by, origin.match, origin.low) == ("base", "closest", 1.0, False)
    assert origin.only_here == origin.only_there == origin.elsewhere == ()
    assert origin.higher is None


def test_a_key_one_side_drops_on_a_paired_part_is_comparable_and_listed_looser():
    base = layered()
    base["parts"]["api"]["litmus"] = "Does it answer a request?"
    origin = compared(parsed(layered()), parsed(base))
    assert origin.match == 1.0
    assert [item.key for item in origin.looser] == ["litmus"]


def test_the_items_of_an_unpaired_part_are_not_comparable():
    custom = layered()
    custom["parts"]["jobs"] = {"path": "jobs", "role": "batch work", "litmus": "Does it run on a schedule?",
                               "imports": {"may": ["shared"]}}
    origin = compared(parsed(custom), parsed(layered()))
    assert origin.counts[:2] == (("parts", 4, 5), ("part_keys", 7, 10))
    assert (origin.only_here, origin.only_there) == (("part jobs",), ())
    assert origin.match == round(12 / 16, 2)


def test_guards_and_profile_keys_are_always_comparable():
    origin = compared(parsed(layered(guards={"no-comments": {}, "closed-tree": {}}, reserved={"ast": "the reader's"})),
                      parsed(layered()))
    assert origin.counts[3:] == (("guards", 2, 2), ("profile", 2, 2))
    assert origin.match == 1.0


def test_each_setting_of_a_held_kind_is_an_item_of_its_own():
    custom = layered()
    custom["parts"]["service"]["holds"] = {"classes": {"names": ["*Service"], "immutable": True, "built_by": ["api"]}}
    assert compared(parsed(custom), parsed(layered())).counts[1] == ("part_keys", 11, 11)


def test_a_tier_folder_written_empty_is_an_item_and_no_folder_is_none():
    architecture = parsed(covered())
    unit = architecture.tiers[0]
    empty = replace(architecture, tiers=(replace(unit, imports_may=()), *architecture.tiers[1:]))
    assert unit.imports_may is None
    assert compared(empty, architecture).counts[2] == ("tiers", 6, 6)
    assert compared(architecture, architecture).counts[2] == ("tiers", 5, 5)


OWN = {"read": "call", "may_not": {"path": ["builtins.print"]}, "message": "{where} prints", "fix": "log it",
       "examples": {"flagged": {"src/billing/api/x.py": "print(1)\n"}, "clean": {"src/billing/api/y.py": "pass\n"}}}
"""A check of the profile's own: no part of it prints."""


def test_a_check_of_the_profile_s_own_is_comparable_only_with_the_same_id():
    base = parsed(layered(checks={"no-print": OWN}))
    assert compared(parsed(layered(checks={"no-print": OWN})), base).counts[4] == ("profile", 2, 2)
    assert compared(parsed(layered(checks={"prints": OWN})), base).counts[4] == ("profile", 1, 3)


def test_a_bundled_profile_no_part_pairs_with_is_no_candidate():
    origin = origin_of("mine.yaml", parsed(layered()), False, {"other": bare(web="web")})
    assert (origin.compared, origin.chosen_by, origin.match, origin.counts) == (None, None, None, ())


def test_the_bundled_profile_of_highest_match_is_compared_the_lowest_name_on_a_tie():
    mine = bare(a="a", b="b", c="c")
    bundled = {"far": bare(a="a", x="x", y="y"), "near": bare(a="a", b="b", c="c", d="d"), "mid": bare(a="a", b="b")}
    origin = origin_of("mine.yaml", mine, False, bundled)
    assert (origin.compared, origin.chosen_by, origin.match) == ("near", "closest", 0.75)
    tie = {"zeta": bare(a="a", b="b", c="c", d="d"), "beta": bare(a="a", b="b", c="c", e="e")}
    assert origin_of("mine.yaml", mine, False, tie).compared == "beta"


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_of_highest_match():
    mine = bare(a="a", b="b", c="c")
    bundled = {"alpha": bare(a="a", b="b", c="c"), "beta": bare(a="a")}
    origin = origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled)
    assert (origin.compared, origin.chosen_by, origin.match, origin.higher) == ("beta", "based_on", 0.33, ("alpha", 1.0))
    assert origin_of("mine.yaml", mine, False, bundled).higher is None


def test_based_on_a_bundled_profile_sharing_no_part_is_compared_low_with_no_part_in_common():
    other = replace(bare(web="web"), reserved={"ast": "the reader's"})
    origin = origin_of("mine.yaml", replace(parsed(layered()), based_on="other"), False, {"other": other})
    assert (origin.compared, origin.chosen_by, origin.low) == ("other", "based_on", True)
    assert origin.only_here == ("part api", "part service", "part shared", "part store")
    assert origin.only_there == ("part web",)
    assert origin.looser == (Loosened("reserved", "", "ast", "ast is no longer reserved (reserved.ast)"),)


def test_a_match_of_exactly_75_percent_is_not_low_and_just_below_is():
    base = bare(a="a", b="b", c="c", d="d")
    exact = compared(bare(a="a", b="b", c="c"), base)
    assert (LOW, exact.match, exact.low) == (0.75, 0.75, False)
    litmus = replace(base, parts={**base.parts, "d": replace(base.parts["d"], litmus="Is it d?")})
    below = compared(bare(a="a", b="b", c="c"), litmus)
    assert (below.match, below.low) == (0.6, True)


def test_a_match_that_rounds_to_75_percent_from_below_is_still_low():
    origin = compared(bare(**{f"p{n}": f"p{n}" for n in range(50)}), bare(**{f"p{n}": f"p{n}" for n in range(67)}))
    assert (origin.match, origin.low) == (0.75, True)


def test_the_counts_are_by_kind_in_order():
    counts = compared(parsed(covered()), parsed(layered())).counts
    assert [kind for kind, _, _ in counts] == ["parts", "part_keys", "tiers", "guards", "profile"]
    assert counts[2] == ("tiers", 0, 5)


def test_a_pair_by_name_at_another_path_is_named_elsewhere():
    custom = layered()
    custom["parts"]["store"]["path"] = "src/<module>/db"
    origin = compared(parsed(custom), parsed(layered()))
    assert origin.elsewhere == ("store: src/*/store there",)
    assert origin.match == 1.0
```

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 120 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py`
Expected: ImportError, `cannot import name 'LOW' from 'xarch.modules.spec.application.logic.looseness'`.

- [ ] **Step 3: Write the failing service tests**

In `tests/modules/spec/application/test_origin.py` (after Task 1's rename), replace:

```python
    origin = controller(BASE).origin("mine.yaml")
    assert (origin.bundled, origin.compared, origin.looser) == (False, "base", ())
    assert origin.baseline_off == origin.guards_off
```

with:

```python
    origin = controller(BASE).origin("mine.yaml")
    assert (origin.bundled, origin.compared, origin.looser) == (False, "base", ())
    assert (origin.chosen_by, origin.match, origin.low) == ("closest", 1.0, False)
    assert origin.baseline_off == origin.guards_off
```

replace:

```python
    assert (origin.compared, origin.baseline_off, origin.looser) == (None, (), ())
```

with:

```python
    assert (origin.compared, origin.match, origin.baseline_off, origin.looser) == (None, None, (), ())
```

and replace the whole test `test_the_closest_bundled_profile_is_the_one_sharing_the_most_parts_the_first_by_name_on_a_tie`
with:

```python
def test_the_closest_bundled_profile_is_the_one_of_highest_match_the_first_by_name_on_a_tie():
    custom = {**OTHER, "parts": {**OTHER["parts"], "core": {"path": "core", "role": "x"},
                                 "store": {"path": "store", "role": "y"}}}
    origin = controller(custom).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by, origin.match, origin.low) == ("base", "closest", 0.48, True)
    assert controller(OTHER).origin("mine.yaml").compared == "other"
    tie = spec_controller(FakeArchitectureFiles({"zeta": OTHER, "alpha": OTHER}, {"mine.yaml": OTHER}, {}))
    assert tie.origin("mine.yaml").compared == "alpha"
```

(`custom` has web, core and store: against `base` 12 of 25 items pair, 0.48; against `other` 3 of 7, 0.43.)

In `tests/modules/spec/application/test_profile_loading.py` replace the module docstring's second line
`bundled profile, whatever it shares most parts with."""` with `bundled profile, whatever bundled profile matches it higher."""`,
and replace:

```python
def test_without_saying_so_a_profile_resembles_the_bundled_one_sharing_most_parts():
    assert controller(MINE).origin("mine.yaml").compared == "base"
```

with:

```python
def test_without_saying_so_a_profile_is_compared_with_the_bundled_one_of_highest_match():
    origin = controller(MINE).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("base", "closest")
```

replace:

```python
    origin = controller(MINE | {"based_on": "other"}).origin("mine.yaml")
    assert origin.compared == "other"
```

with:

```python
    origin = controller(MINE | {"based_on": "other"}).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("other", "based_on")
```

and replace:

```python
    origin = controller(MINE | {"based_on": "base"}).origin("mine.yaml")
    assert origin.compared == "base"
```

with:

```python
    origin = controller(MINE | {"based_on": "base"}).origin("mine.yaml")
    assert (origin.compared, origin.chosen_by) == ("base", "based_on")
```

In `tests/modules/spec/application/test_check.py`, after the `OFF = (...)` tuple (line 19-20) add:

```python
SELF = (("parts", 2, 2), ("part_keys", 3, 3), ("tiers", 0, 0), ("guards", 0, 0), ("profile", 2, 2))
"""The counts of base against itself: everything check reads under it has a counterpart."""
COPY = Origin("mine.yaml", False, "base", OFF, OFF, (), "based_on", 1.0, False, SELF)
"""The origin of a copy of base that says it is based on it."""
```

and in `test_check_profile`'s parameters replace
`ProfileChecked("mine.yaml", (), 2, Origin("mine.yaml", False, "base", OFF, OFF, ())),` with
`ProfileChecked("mine.yaml", (), 2, COPY),`, and replace:

```python
                                         "(parts.core.imports.may)"),), 3,
                                Origin("mine.yaml", False, "base", OFF, OFF, ())),
```

with:

```python
                                         "(parts.core.imports.may)"),), 3, COPY),
```

- [ ] **Step 4: Run them to see them fail**

Run: `timeout 120 uv run pytest -q tests/modules/spec/application/test_origin.py tests/modules/spec/application/test_profile_loading.py tests/modules/spec/application/test_check.py`
Expected: FAIL: `chosen_by` and `match` are still None, so the copy test and the highest-match test of
`test_origin.py`, the three `chosen_by` asserts of `test_profile_loading.py` and both `COPY` params of `test_check.py`
fail (the `zeta`/`alpha` tie happens to pass under the old rule too: both share the one part).

- [ ] **Step 5: Write the items, the pairing and the match**

In `xarch/modules/spec/application/logic/looseness.py`, replace the imports

```python
from collections.abc import Mapping

from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import LINE, LITMUS, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture, DeadCode, NoTwins
from xarch.profile_values.placement import Target
```

with:

```python
from collections.abc import Collection, Mapping
from dataclasses import replace
from fractions import Fraction

from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, LINE, LITMUS, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture, DeadCode, NoTwins, PackageOnly, Part, Tier
from xarch.profile_values.placement import Target
```

After the docstring of `LOOSER` (`"""Every key a way a profile is looser is listed under, each said by a sentence of its
own."""`) add:

```python
LOW = 0.75
"""The match below which a comparison is low: less than three in four of the things `check` reads under either
profile have a counterpart in the other, so how the profile is looser says little of how `check` would do under the
other."""
PARTS, PART_KEYS, TIERS, GUARDS, PROFILE = "parts", "part_keys", "tiers", "guards", "profile"
COUNTED = (PARTS, PART_KEYS, TIERS, GUARDS, PROFILE)
"""The kinds the items of a match are counted by, in the order they are said: the parts, the keys of a part, the tiers
and their entries, the guards switched on, and the keys of the profile as a whole."""
CHECKS = "checks"
"""The address of an item that is a check of the profile's own, which has a counterpart only in a check of its id."""
BOTH, HERE, THERE = "both", "here", "there"
"""Whom an item is counted for: both profiles, as one comparable item; or only the profile compared, or only the one it
is compared with."""
Item = tuple[str, str | None, str | None, tuple[object, ...]]
"""(kind, part, tier, address): one thing `check` reads under a profile, one of COUNTED, held by its part, its tier,
both, or neither (a guard, a key of the profile as a whole); the address says which thing it is."""
```

Replace the whole function `_closest` (from `def _closest(` through its `return min(...) if best else None`) with:

```python
def _paired_parts(mine: Architecture, other: Architecture) -> dict[str, str]:
    """Each part of mine paired with a part of other: the one of the same name, else the first of other's, in its
    order, at the same path as written that no part of mine is paired with yet; a part pairs at most once."""
    pairs = {name: name for name in mine.parts if name in other.parts}
    for name, part in mine.parts.items():
        if name not in pairs:
            found = next((theirs for theirs, there in other.parts.items()
                          if theirs not in pairs.values() and there.path == part.path), None)
            if found is not None:
                pairs[name] = found
    return pairs


def _paired_tiers(mine: Architecture, other: Architecture, parts: Mapping[str, str]) -> dict[str, str]:
    """Each tier of mine paired with a tier of other: the one of the same name, else the first of other's whose
    subject, its parts read through the pairing of parts, is the same; a tier pairs at most once."""
    names = {tier.name for tier in other.tiers}
    pairs = {tier.name: tier.name for tier in mine.tiers if tier.name in names}
    same = {name: name for name in other.parts}
    for tier in mine.tiers:
        if tier.name not in pairs:
            found = next((there.name for there in other.tiers
                          if there.name not in pairs.values() and _subject(there, same) == _subject(tier, parts)), None)
            if found is not None:
                pairs[tier.name] = found
    return pairs


def _subject(tier: Tier, parts: Mapping[str, str]) -> frozenset[tuple[str | None, tuple[str, ...]]]:
    """What a tier tests, each part by the name parts gives it (None for a part it gives none)."""
    return frozenset((parts.get(subject.part), subject.sub) for subject in tier.subject)


def _items(architecture: Architecture) -> list[Item]:
    """Every thing `check` reads under the architecture, one item each."""
    packaged = {name for guard in architecture.guards if isinstance(guard, PackageOnly) for name in guard.parts}
    found: list[Item] = []
    for name, part in architecture.parts.items():
        found.append((PARTS, name, None, ("part",)))
        found += [(PART_KEYS, name, None, key) for key in _part_keys(architecture, name, part, name in packaged)]
    for tier in architecture.tiers:
        found.append((TIERS, None, tier.name, ("tier",)))
        found += [(TIERS, subject.part, tier.name, ("subject", subject.sub)) for subject in tier.subject]
        found += [(TIERS, None, tier.name, (key,)) for key in _tier_keys(tier)]
    found += [(GUARDS, None, None, (KEY[type(guard)],)) for guard in architecture.guards]
    found += [(PROFILE, None, None, key) for key in _profile_keys(architecture)]
    return found


def _part_keys(architecture: Architecture, name: str, part: Part, packaged: bool) -> list[tuple[object, ...]]:
    """The keys of a part that hold a value, each with the target, kind or setting it is about."""
    libraries = architecture.imports_libraries
    written = {"imports.may": bool(architecture.rules.get(name)),
               "imports.libraries": libraries is not None and name in libraries,
               "imports.must": bool(part.imports_must), "uses.never": bool(architecture.uses_never.get(name)),
               "untested": bool(part.untested), LITMUS: bool(part.litmus), "shared": part.shared is not None,
               "entry": part.entry, "package_only": packaged}
    keys: list[tuple[object, ...]] = [(key,) for key, held in written.items() if held]
    keys += [("imports.may.types_only", target) for target in part.imports_types_only]
    for held in part.holds:
        settings = {"names": bool(held.names), "immutable": held.immutable, "built_by": bool(held.built_by)}
        keys += [("holds", held.kind), *(("holds", held.kind, key) for key, on in settings.items() if on)]
    return keys


def _tier_keys(tier: Tier) -> list[str]:
    """The keys of a tier that hold a value; a folder's imports.may written empty is one, no folder is none."""
    written = {"imports.types_only": bool(tier.imports_types_only), "uses.apply_never": tier.apply_never,
               "imports.also": bool(tier.imports_also), "imports.must": bool(tier.imports_must),
               "imports.may": tier.imports_may is not None, "plain_tables": tier.plain_tables}
    return [key for key, held in written.items() if held]


def _profile_keys(architecture: Architecture) -> list[tuple[object, ...]]:
    """The keys of the profile as a whole that hold a value, each entry of a list or a map its own."""
    framework = architecture.framework
    written = {"libraries": architecture.imports_libraries is not None,
               "testing.skips": framework is not None and bool(framework.skips), "fakes": architecture.fakes is not None}
    keys: list[tuple[object, ...]] = [(key,) for key, held in written.items() if held]
    keys += [("reserved", name) for name in architecture.reserved]
    keys += [("files", file.path) for file in architecture.files]
    keys += [("excluded", folder.path) for folder in architecture.excluded]
    keys += [(CHECKS, name) for name in architecture.checks]
    return keys


def _counted(items: list[Item], parts: Mapping[str, str], tiers: Mapping[str, str], checks: Collection[str],
             side: str) -> set[tuple[object, ...]]:
    """Each item of one side as it is counted. parts and tiers give each paired holder of the side the name it has in
    the profile compared, and checks are the ids of the checks the other side writes: a comparable item is keyed by
    those names, a target in it read through them too, so that the copy each side has is one; any other item is keyed
    by its side."""
    keys: set[tuple[object, ...]] = set()
    for kind, part, tier, address in items:
        if ((part is None or part in parts) and (tier is None or tier in tiers)
                and (address[0] != CHECKS or address[1] in checks)):
            keys.add((BOTH, kind, None if part is None else parts[part], None if tier is None else tiers[tier],
                      _read(address, parts)))
        else:
            keys.add((side, kind, part, tier, address))
    return keys


def _read(address: tuple[object, ...], parts: Mapping[str, str]) -> tuple[object, ...]:
    """An address with the part of each target in it named as parts gives it (unchanged when it gives none)."""
    return tuple(_into(step, parts) if isinstance(step, Target) else step for step in address)


def _counts(mine: Architecture, other: Architecture) -> tuple[tuple[str, int, int], ...]:
    """For each of COUNTED, in order: how many items of either profile have a counterpart in the other, and how many
    items there are, an item both have counted once."""
    parts = _paired_parts(mine, other)
    tiers = _paired_tiers(mine, other, parts)
    keys = (_counted(_items(mine), {name: name for name in parts}, {name: name for name in tiers}, other.checks, HERE)
            | _counted(_items(other), {theirs: name for name, theirs in parts.items()},
                       {theirs: name for name, theirs in tiers.items()}, mine.checks, THERE))
    return tuple((kind, sum(1 for key in keys if key[1] == kind and key[0] == BOTH),
                  sum(1 for key in keys if key[1] == kind)) for kind in COUNTED)


def _share(counts: tuple[tuple[str, int, int], ...]) -> Fraction:
    """The match: the comparable items over all of them, as an exact fraction."""
    every = sum(total for _, _, total in counts)
    return Fraction(sum(comparable for _, comparable, _ in counts), every) if every else Fraction(0)


def _unpaired(mine: Architecture, parts: Collection[str], tiers: Collection[str]) -> tuple[str, ...]:
    """The parts, then the tiers, of mine that are not among those paired, each by name."""
    return (*(f"part {name}" for name in sorted(mine.parts) if name not in parts),
            *(f"tier {name}" for name in sorted(tier.name for tier in mine.tiers) if name not in tiers))


def _elsewhere(mine: Architecture, other: Architecture) -> tuple[str, ...]:
    """Each part of mine that other has by the same name at another path, with other's path, in mine's order."""
    return tuple(f"{name}: {'/'.join(other.parts[name].path)} there" for name, part in mine.parts.items()
                 if name in other.parts and other.parts[name].path != part.path)


def _into(target: Target, parts: Mapping[str, str]) -> Target:
    """A target with its part named as parts gives it (unchanged when it gives none)."""
    return replace(target, part=parts.get(target.part, target.part))
```

- [ ] **Step 6: Choose by the match, and fill the origin**

Replace the whole function `origin_of` with:

```python
def origin_of(location: str, architecture: Architecture, bundled: bool,
              others: Mapping[str, Architecture]) -> Origin:
    """Where the architecture at location comes from: a bundled one is its own baseline; a custom one is compared with
    the one of others, the bundled architectures by name, it says it is based on, else the one of highest match (the
    first by name on a tie, one no part pairs with never), and is looser than it in the ways it says."""
    off = _guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    shares = {name: _share(_counts(architecture, other)) for name, other in others.items()
              if _paired_parts(architecture, other)}
    best = max(shares.values(), default=Fraction(0))
    highest = min((name for name, share in shares.items() if share == best), default=None)
    if architecture.based_on in others:
        name, chosen_by = architecture.based_on, BASED_ON
    elif highest is not None:
        name, chosen_by = highest, CLOSEST
    else:
        return Origin(location, False, None, off, (), ())
    base = others[name]
    counts = _counts(architecture, base)
    share = _share(counts)
    parts = _paired_parts(architecture, base)
    tiers = _paired_tiers(architecture, base, parts)
    looser = tuple(Loosened(key, part, what, _sentence(key, part, what)) for key, part, what in _looser(architecture, base))
    return Origin(location, False, name, off, tuple(g for g in off if g in _guards_off(base)), looser,
                  chosen_by=chosen_by, match=round(float(share), 2), low=share < LOW or not parts, counts=counts,
                  only_here=_unpaired(architecture, parts, tiers),
                  only_there=_unpaired(base, parts.values(), tiers.values()),
                  elsewhere=_elsewhere(architecture, base),
                  higher=(highest, round(float(best), 2)) if highest is not None and best > share else None)
```

- [ ] **Step 7: Run the tests to see them pass**

Run: `timeout 300 uv run pytest -q tests/modules/spec tests/modules/rules tests/cli`
Expected: all pass.

Run: `uv run ruff check && uv run xarch check >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 8: Reproduce the spec's table**

Run:

```bash
uv run python - <<'EOF'
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.application.logic.looseness import _counts, _share
cli, web = load_architecture("cli"), load_architecture("web")
for name in ("architecture.yaml", "tests/bootstrap/corpora/stress.yaml", "cli"):
    mine = load_architecture(name)
    for other, base in (("cli", cli), ("web", web)):
        if name != other:
            counts = _counts(mine, base)
            print(name, other, counts, _share(counts), f"{float(_share(counts)):.1%}")
EOF
```

Expected, exactly:

```
architecture.yaml cli (('parts', 12, 15), ('part_keys', 72, 91), ('tiers', 21, 31), ('guards', 11, 11), ('profile', 9, 9)) 125/157 79.6%
architecture.yaml web (('parts', 11, 16), ('part_keys', 67, 96), ('tiers', 21, 31), ('guards', 11, 11), ('profile', 9, 9)) 119/163 73.0%
tests/bootstrap/corpora/stress.yaml cli (('parts', 11, 14), ('part_keys', 75, 93), ('tiers', 19, 30), ('guards', 11, 11), ('profile', 10, 10)) 63/79 79.7%
tests/bootstrap/corpora/stress.yaml web (('parts', 10, 15), ('part_keys', 70, 97), ('tiers', 19, 30), ('guards', 11, 11), ('profile', 10, 10)) 120/163 73.6%
cli web (('parts', 11, 13), ('part_keys', 64, 74), ('tiers', 16, 18), ('guards', 11, 11), ('profile', 6, 6)) 54/61 88.5%
```

(`63/79` is `126/158` reduced, `54/61` is `108/122`.) Any other number: stop and report it with the table; never
change an item rule to reach it.

- [ ] **Step 9: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py \
  tests/modules/spec/application/test_origin.py tests/modules/spec/application/test_profile_loading.py \
  tests/modules/spec/application/test_check.py
git commit -m "A custom profile's comparison has a match, the share of what check reads under either profile with a counterpart in the other, parts paired by name then path and tiers by name then subject, low below 75%; without based_on it is compared with the bundled profile of highest match, the lowest name on a tie, and based_on names the higher one when there is one

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The looser list compares paired parts and tiers

**Files:**
- Modify: `xarch/modules/spec/application/logic/looseness.py` (module docstring `:1-23`, `_looser`)
- Test: `tests/modules/spec/application/logic/test_looseness.py`

**Interfaces:**
- Consumes: `_paired_parts`, `_paired_tiers`, `_into` (Task 2).
- Produces: `_looser(custom: Architecture, base: Architecture) -> list[Looser]`, same signature, now over the pairing.

- [ ] **Step 1: Record today's looser lists of the repo's profiles**

```bash
cat > /tmp/looser-5-1.py <<'EOF'
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.application.logic.looseness import _looser
for name in ("architecture.yaml", "tests/bootstrap/corpora/stress.yaml", "cli", "web"):
    for other in ("cli", "web"):
        print(name, other, _looser(load_architecture(name), load_architecture(other)))
EOF
uv run python /tmp/looser-5-1.py > /tmp/looser-5-1-before.txt && wc -l /tmp/looser-5-1-before.txt
```

Expected: `8 /tmp/looser-5-1-before.txt`.

- [ ] **Step 2: Write the failing tests**

In `tests/modules/spec/application/logic/test_looseness.py`, after the helper `compared` (added in Task 2) add:

```python
def renamed(document: dict, old: str, new: str) -> dict:
    """The document with the part old named new, at the same place in the order and the same path."""
    document["parts"] = {new if name == old else name: part for name, part in document["parts"].items()}
    return document
```

and append at the end of the file:

```python
def test_a_part_renamed_in_place_pairs_by_its_path_and_is_compared_under_its_own_name():
    custom = renamed(layered(), "api", "routes")
    custom["parts"]["routes"]["imports"] = {"may": ["service", "store"]}
    origin = compared(parsed(custom), parsed(layered()))
    assert (origin.match, origin.only_here, origin.only_there) == (1.0, (), ())
    assert origin.looser == (
        Loosened("imports.may", "routes", "store", "routes may also import store (parts.routes.imports.may)"),)


def test_a_target_naming_a_part_renamed_in_place_is_read_through_the_pairing():
    base = layered()
    base["parts"]["service"]["imports"] = {"may": ["store", "shared", "api"]}
    custom = renamed(layered(), "api", "routes")
    custom["parts"]["service"]["imports"] = {"may": ["store", "shared", "routes"]}
    origin = compared(parsed(custom), parsed(base))
    assert (origin.match, origin.looser) == (1.0, ())


def test_a_tier_renamed_with_the_same_subject_pairs_by_subject():
    base = covered()
    base["tiers"]["unit"]["uses"] = {"apply_never": True}
    custom = covered()
    custom["tiers"] = {"logic" if name == "unit" else name: tier for name, tier in custom["tiers"].items()}
    custom["parts"]["service"]["tests"] = "logic"
    origin = compared(parsed(custom), parsed(base))
    assert (origin.match, origin.only_here, origin.only_there) == (1.0, (), ())
    assert origin.looser == (Loosened("uses.apply_never", "logic", "", "the logic tests are no longer held to their "
                                                                       "part's never list (tiers.logic.uses.apply_never)"),)
```

- [ ] **Step 3: Run them to see them fail**

Run: `timeout 120 uv run pytest -q tests/modules/spec/application/logic/test_looseness.py -k renamed`
Expected: 3 FAIL: the renamed `routes` is compared with nothing, so its added target is not listed (`() == (Loosened(...),)`);
the target `routes` is listed looser (`service may also import routes`); the renamed tier's dropped `apply_never` is
not listed.

- [ ] **Step 4: Compare over the pairing**

Replace the whole function `_looser` (from `def _looser(` through its `return found`) with:

```python
def _looser(custom: Architecture, base: Architecture) -> list[Looser]:
    member = custom.language.checked.member
    pairs = _paired_parts(custom, base)
    back = {theirs: name for name, theirs in pairs.items()}
    shared = [name for name in custom.parts if name in pairs]
    found: list[Looser] = []
    for name in shared:
        before = base.rules.get(pairs[name], ())
        found += [("imports.may", name, _shown(t)) for t in custom.rules.get(name, ())
                  if not any(_covers(b, _into(t, pairs)) for b in before)]
    for name in shared:
        allows = [_into(c, pairs) for c in custom.rules.get(name, ())]
        marks = [_into(c, pairs) for c in custom.parts[name].imports_types_only]
        found += [("imports.may.types_only", name, _shown(_into(t, back))) for t in base.parts[pairs[name]].imports_types_only
                  if any(_covers(c, t) for c in allows) and not any(_covers(c, t) for c in marks)]
    if base.imports_libraries is not None:
        if custom.imports_libraries is None:
            found.append(("imports.libraries", "", ""))
        else:
            found += [("imports.libraries", name, package) for name in shared for package in custom.imports_libraries.get(name, ())
                      if package not in base.imports_libraries.get(pairs[name], ())]
    for name in shared:
        kept = custom.uses_never.get(name, ())
        found += [("uses.never", name, outside_text(banned, member)) for banned in base.uses_never.get(pairs[name], ())
                  if not any(banned[:len(entry)] == entry for entry in kept)]
    for name in shared:
        before, now = base.parts[pairs[name]].imports_must, custom.parts[name].imports_must
        if before and not now:
            found.append(("imports.must", name, ""))
        else:
            found += [("imports.must", name, _shown(t)) for t in now if before and _into(t, pairs) not in before]
    found += [("untested", name, "") for name in shared
              if custom.parts[name].untested and not base.parts[pairs[name]].untested]
    found += [(LITMUS, name, "") for name in shared if base.parts[pairs[name]].litmus and not custom.parts[name].litmus]
    paired = _paired_tiers(custom, base, pairs)
    tiers = {paired[tier.name]: tier for tier in custom.tiers if tier.name in paired}
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None:
            marked = {pairs.get(part, part) for part in mine.imports_types_only}
            found += [("imports.types_only", mine.name, back.get(part, part)) for part in tier.imports_types_only
                      if part not in marked]
            found += [("imports.also", mine.name, _shown(t)) for t in mine.imports_also
                      if not any(_covers(b, _into(t, pairs)) for b in tier.imports_also)]
    found += [("uses.apply_never", tiers[tier.name].name, "") for tier in base.tiers
              if tier.apply_never and tier.name in tiers and not tiers[tier.name].apply_never]
    skips = custom.framework.skips if custom.framework is not None else ()
    if base.framework is not None:
        found += [("testing.skips", "", outside_text(name, member)) for name in base.framework.skips if name not in skips]
    files = {file.path: file for file in custom.files}
    found += [("files.pinned", "", "/".join(file.path)) for file in base.files
              if file.pinned and file.path in files and not files[file.path].pinned]
    found += [("reserved", "", name) for name in base.reserved if name not in custom.reserved]
    accepted = _known(base)
    found += [("known", "", entry) for entry in _known(custom) if entry not in accepted]
    translators = _translators(base)
    found += [("translated", part, "") for part in _translators(custom) if pairs.get(part, part) not in translators]
    found += [("review.never", "", path) for path in base.never if path not in custom.never]
    found += [("review.mask", "", text) for text in base.mask if text not in custom.mask]
    found += [("evals.placement.lines", name, f"{custom.lines.get(name, LINE):.2f}") for name in shared
              if custom.lines.get(name, LINE) < base.lines.get(pairs[name], LINE)]
    return found
```

- [ ] **Step 5: Say it in the module docstring**

Replace the module docstring of `looseness.py` (from the first `"""How a profile compares with the bundled ones` down to
its closing `"""`, just above `from __future__ import annotations`) with:

```python
"""How a profile compares with the bundled ones: the one it is compared with, how much the two have in common (its
match), the guards it leaves off, and every way it is looser than that one.

A custom profile is compared with the bundled profile its `based_on` names, else with the one of highest match, the
first by name on a tie; one no part pairs with is no candidate, and with none left nothing is compared. The match is
the share of the items of either profile, one per thing `check` reads, that have a counterpart in the other: each part;
each key of a part that holds a value (imports.may, imports.libraries, imports.must, each target marked types_only,
uses.never, each kind of holds and each setting it writes, untested, litmus, shared, entry, package_only); each tier,
each entry of its subject and each of its keys that holds a value; each guard switched on; and each key of the profile
as a whole (libraries, testing.skips, each reserved module, files entry and excluded folder, fakes, each check of its
own). Parts pair by name, then by the same layout path; tiers by name, then by the same subject, its parts read
through the pairing; each at most once. An item has a counterpart when every part and tier holding it pairs (a check
of the profile's own, when the other writes one of its id), so a key one side drops on a paired holder still has one.
A match below LOW, or one with no part paired, is low.

Looser is compared only on the parts and tiers that pair, the part of a target read through the pairing (a part
renamed in place is compared, and said, under the custom profile's name), and on the files of the same path, and only
in these ways, each one entry: a target added to a part's `imports.may`
that no target of the bundled one covers (a target covers what lies below it: the same part and scope, its path a
start of the added one's, and no name pattern or the same one; so a name pattern added to a target, or a folder below
it, narrows it, and is not looser); a `types_only` mark dropped from an entry of a part's `imports.may` whose target
the part still may import (some entry covers it) and no mark of its covers; an outside package added to a part's
`imports.libraries`, or `libraries` dropped as a whole; a target added to a part's `imports.must`, or the key dropped
from a part that has it; a name the bundled
`uses.never` list of a part holds that no entry of the custom list covers (`time` covers `time.time`); a part newly
marked `untested`; a part dropped from a tier's `imports.types_only`; a target added to a tier's `imports.also` that no
target of the bundled tier's covers; a tier no longer `uses.apply_never`; a name dropped from `testing.skips`; a `files`
entry no longer `pinned`; a name the bundled profile `reserved` holds that the custom one does not; a part the bundled
profile gives a `litmus` that the custom one redefines without one; a public name `guards.dead-code.known` accepts as
only the tests' that the bundled profile's does not; a part `guards.no-twins.translated` lists that the bundled
profile's does not; a path `review.never` holds back, or a text `review.mask` hides, in the bundled profile that the
custom one does not write (each compared as written: it sends more); a part whose line under `evals.placement.lines`
is below the one the bundled profile gives it (written, else LINE: it flags less). Anything stricter, and what is
compared in no way above (the layout, new parts, the guards' other parameters, `fakes`), is not listed.
"""
```

- [ ] **Step 6: Run the tests to see them pass, and the repo's looser lists unchanged**

Run: `timeout 300 uv run pytest -q tests/modules/spec tests/modules/rules tests/cli`
Expected: all pass.

Run: `uv run python /tmp/looser-5-1.py | diff /tmp/looser-5-1-before.txt - && echo SAME`
Expected: `SAME`.

Run: `uv run ruff check && uv run xarch check >/dev/null; echo "exit $?"`
Expected: `All checks passed!` and `exit 0`.

- [ ] **Step 7: Commit**

```bash
git add xarch/modules/spec/application/logic/looseness.py tests/modules/spec/application/logic/test_looseness.py
git commit -m "The ways a profile is looser are compared on the parts and tiers that pair, every part name across the two read through the pairing, so a part or tier renamed in place is still compared under its own name; with every pair by name the list is unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `profile check` and `check` say the match, in text and JSON

**Files:**
- Modify: `xarch/cli/reports/profile_report.py` (docstring `:10-14`, imports `:25-35`, `origin_words` `:185-191`,
  `check_lines` `:194-212`, `check_document` `:246-259`)
- Modify: `xarch/cli/reports/report.py` (import `:19`, `_enforcement_lines` `:81`, `_enforcement_document` `:145`)
- Test: `tests/cli/reports/test_profile_report.py`, `tests/cli/reports/test_report.py`
- Test: `tests/bootstrap/test_profile_check.py`, `tests/bootstrap/test_check_enforcement.py`

**Interfaces:**
- Consumes: `Origin`/`Resemblance` fields and `CLOSEST` (Task 1); the real values filled by Task 2.
- Produces (in `profile_report.py`, read by `report.py`): `compared_words(origin: Origin | Resemblance) -> str`,
  `percent(match: float | None) -> str`, `low_reason(origin: Origin | Resemblance) -> str`,
  `compared_document(origin: Origin | Resemblance) -> dict[str, Any] | None`. `origin_words` becomes the private
  `_origin_words` (only its own file uses it once `report.py` reads `compared_words`; a public name only the tests use
  is a `dead-code` weak finding that fails `xarch check --strict`).

- [ ] **Step 1: Write the failing `profile check` report tests**

In `tests/cli/reports/test_profile_report.py`:

- add `from dataclasses import replace` after `import json`;
- in the import from `xarch.cli.reports.profile_report` remove the line `    origin_words,`;
- replace `from xarch.modules.rules.contract import ChecksHeld, ProfileHeld, ProfileUnloaded, Resemblance, Reviewed`
  with `from xarch.modules.rules.contract import ChecksHeld, Loosened, ProfileHeld, ProfileUnloaded, Resemblance, Reviewed`;
- in the import from `xarch.modules.spec.contract` remove the line `    Origin,`;
- replace the whole parametrized test `test_where_a_profile_comes_from_is_said_the_same_by_profile_check_and_by_check`
  (its `@pytest.mark.parametrize("origin, resemblance, words", [` through its two-line body) with:

```python
COUNTS = (("parts", 12, 15), ("part_keys", 72, 91), ("tiers", 21, 31), ("guards", 11, 11), ("profile", 9, 9))
"""The counts of xarch's own profile against cli."""
MATCH = ("  match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, "
         "9 of 9 profile keys sit where both profiles have them")
"""The match line of a profile based on cli that matches it at 80%, with COUNTS."""


def based_on_cli(**changes) -> Resemblance:
    """A custom profile based on cli, matching it at 80% with COUNTS and nothing unpaired; the fields given replaced."""
    return replace(Resemblance(False, "cli", (), "based_on", 0.8, False, COUNTS), **changes)


def checked(resemblance: Resemblance) -> list[str]:
    """What `profile check` says of a valid profile that resembles the bundled ones as given, but its verdict."""
    return check_lines(ProfileHeld(Reviewed("mine.yaml", (), 1, resemblance), ChecksHeld((), 0)))[:-1]


def matched(resemblance: Resemblance) -> list[str]:
    """The lines `profile check` says of the match: those between the examples and the comparison."""
    return checked(resemblance)[4:-1]


@pytest.mark.parametrize("resemblance, words", [
    pytest.param(Resemblance(True), "bundled", id="a bundled profile"),
    pytest.param(based_on_cli(), "custom; based_on: cli", id="a custom one names the profile it is based on"),
    pytest.param(based_on_cli(chosen_by="closest"), "custom; closest bundled: cli, match 80%",
                 id="a custom one names the bundled profile of highest match, with the match"),
    pytest.param(Resemblance(False), "custom; no bundled profile resembles it",
                 id="a custom one that resembles none says so"),
])
def test_profile_check_is_headed_with_where_the_profile_comes_from(resemblance, words):
    assert checked(resemblance)[0] == f"checking mine.yaml ({words})"


def test_the_match_is_said_with_its_counts_and_what_pairs_with_nothing_on_either_side_before_the_comparison():
    resemblance = based_on_cli(only_here=("part main", "part profile-values", "part reports", "tier wired"),
                               only_there=("tier rendering",))
    assert checked(resemblance)[4:] == [
        MATCH, "    only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering",
        "  compared: no looser than cli"]


@pytest.mark.parametrize("only_here, only_there, said", [
    pytest.param((), ("part web", "tier rendering"), ["    only in cli: part web; tier rendering"],
                 id="an empty side is left out"),
    pytest.param(("tier wired",), (), ["    only here: tier wired"], id="an empty group is left out"),
    pytest.param((), (), [], id="with both sides empty the line is left out"),
    pytest.param(tuple(f"part p{n}" for n in range(7)), (), ["    only here: parts p0, p1, p2, p3, p4 and 2 more"],
                 id="past five names a group counts the rest"),
])
def test_what_pairs_with_nothing_is_said_by_side_and_by_group(only_here, only_there, said):
    assert matched(based_on_cli(only_here=only_here, only_there=only_there)) == [MATCH, *said]


def test_a_part_of_the_same_name_at_another_path_is_said_past_five_counting_the_rest():
    elsewhere = tuple(f"p{n}: modules/*/p{n} there" for n in range(7))
    assert matched(based_on_cli(elsewhere=elsewhere)) == [
        MATCH, "    same name, other path: p0: modules/*/p0 there, p1: modules/*/p1 there, p2: modules/*/p2 there, "
               "p3: modules/*/p3 there, p4: modules/*/p4 there and 2 more"]


@pytest.mark.parametrize("resemblance, said", [
    pytest.param(based_on_cli(compared="web", match=0.73, low=True),
                 "    low: 27% of what check reads under either profile has nothing to compare with in the other, so the "
                 "list below says little about how check would do under web",
                 id="by the share that has nothing to compare with"),
    pytest.param(based_on_cli(compared="web", match=0.75, low=True),
                 "    low: 25% of what check reads under either profile has nothing to compare with in the other, so the "
                 "list below says little about how check would do under web",
                 id="a match just below 75% that rounds to it is still low"),
    pytest.param(based_on_cli(compared="web", match=0.5, low=True, counts=(("parts", 0, 4), *COUNTS[1:])),
                 "    low: no part in common, so the list below says little about how check would do under web",
                 id="with no part in common"),
])
def test_a_low_match_says_why_the_comparison_says_little(resemblance, said):
    assert matched(resemblance)[-1] == said


def test_a_bundled_profile_of_higher_match_than_the_one_based_on_is_named_with_its_match():
    assert matched(based_on_cli(higher=("web", 0.88))) == [MATCH, "    web matches 88%"]


def test_nothing_of_a_match_is_said_when_nothing_is_compared():
    assert matched(Resemblance(True)) == matched(Resemblance(False)) == []


def test_the_json_of_profile_check_holds_every_field_of_the_profile_compared_with():
    resemblance = based_on_cli(looser=(Loosened("untested", "api", "", "api is newly marked untested (parts.api.untested)"),),
                               only_here=("part main", "tier wired"), only_there=("tier rendering",),
                               elsewhere=("store: src/*/store there",), higher=("web", 0.88))
    held = ProfileHeld(Reviewed("mine.yaml", (), 1, resemblance), ChecksHeld((), 0))
    assert json.loads(check_document(held))["compared_with"] == {
        "profile": "cli", "chosen_by": "based_on", "match": 0.8, "low": False,
        "counts": {"parts": [12, 15], "part_keys": [72, 91], "tiers": [21, 31], "guards": [11, 11], "profile": [9, 9]},
        "only_here": ["part main", "tier wired"], "only_there": ["tier rendering"],
        "elsewhere": ["store: src/*/store there"], "higher": {"profile": "web", "match": 0.88},
        "looser": [{"key": "untested", "part": "api", "what": "", "sentence": "api is newly marked untested (parts.api.untested)"}]}
    bundled = ProfileHeld(Reviewed("web", (), 1, Resemblance(True)), ChecksHeld((), 0))
    assert json.loads(check_document(bundled))["compared_with"] is None
```

- [ ] **Step 2: Run them to see them fail**

Run: `timeout 120 uv run pytest -q tests/cli/reports/test_profile_report.py`
Expected: FAIL: the header still reads `custom; closest bundled: cli` for `based_on`, no `match:` line is written,
and `compared_with` has only `profile` and `looser`.

- [ ] **Step 3: Write the words, the match lines and the shared JSON object**

In `xarch/cli/reports/profile_report.py`, in the module docstring replace:

```
profile's own) and compared_with {"profile", "looser"} (null for a bundled profile or one that resembles none), each
looser entry {"key", "part", "what", "sentence"}.
```

with:

```
profile's own) and compared_with {"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there",
"elsewhere", "higher", "looser"} (null for a bundled profile or one that resembles none), counts {"parts",
"part_keys", "tiers", "guards", "profile"} each [comparable, all], higher null or {"profile", "match"}, each looser
entry {"key", "part", "what", "sentence"}; `check`'s JSON holds the same compared_with under enforcement.profile.
```

In the import from `xarch.modules.spec.contract` add `    CLOSEST,` as the first name (before `    FilesTaken,`).

Replace the whole function `origin_words` with:

```python
NAMED = 5
"""How many names a line of the match names in a group before it counts the rest."""
COUNTED = {"parts": "parts", "part_keys": "part keys", "tiers": "tier entries", "guards": "guards",
           "profile": "profile keys"}
"""How the match line says each kind of thing it counts, by the kind."""


def _origin_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as `profile check` heads it: bundled, or custom and the profile it is
    compared with and why (with the match, when it is the closest), if any."""
    if origin.bundled:
        return "bundled"
    if origin.compared is None:
        return "custom; no bundled profile resembles it"
    if origin.chosen_by == CLOSEST:
        return f"custom; closest bundled: {origin.compared}, match {percent(origin.match)}"
    return f"custom; {origin.chosen_by}: {origin.compared}"


def compared_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as the enforcement section of `check` says it: bundled, or custom and the
    profile it is compared with, why, and the match, if any."""
    if origin.bundled or origin.compared is None:
        return _origin_words(origin)
    return f"custom; compared with {origin.compared}, {origin.chosen_by}; match {percent(origin.match)}"


def percent(match: float | None) -> str:
    """A match as a whole percentage, e.g. 80%."""
    return f"{round((match or 0) * 100)}%"


def low_reason(origin: Origin | Resemblance) -> str:
    """Why a low match says little of how `check` would do under the profile compared with."""
    why = ("no part in common" if not next((comparable for kind, comparable, _ in origin.counts if kind == "parts"), 0)
           else f"{100 - round((origin.match or 0) * 100)}% of what check reads under either profile has nothing to "
                "compare with in the other")
    return f"{why}, so the list below says little about how check would do under {origin.compared}"


def _match_lines(resemblance: Resemblance) -> list[str]:
    """The match with the profile compared with, its counts, what pairs with nothing, the parts at another path, and
    whether it is low or another bundled profile matches higher; nothing when nothing is compared."""
    if resemblance.bundled or resemblance.compared is None:
        return []
    counts = ", ".join(f"{comparable} of {every} {COUNTED[kind]}" for kind, comparable, every in resemblance.counts)
    lines = [f"  match: {percent(resemblance.match)} with {resemblance.compared} ({resemblance.chosen_by}): {counts} "
             "sit where both profiles have them"]
    sides = [f"{label}: {_unpaired(names)}" for label, names in (("only here", resemblance.only_here),
                                                                  (f"only in {resemblance.compared}", resemblance.only_there))
             if names]
    if sides:
        lines.append(f"    {'. '.join(sides)}")
    if resemblance.elsewhere:
        lines.append(f"    same name, other path: {_named(resemblance.elsewhere)}")
    if resemblance.low:
        lines.append(f"    low: {low_reason(resemblance)}")
    if resemblance.higher is not None:
        lines.append(f"    {resemblance.higher[0]} matches {percent(resemblance.higher[1])}")
    return lines


def _unpaired(names: Sequence[str]) -> str:
    """The parts, then the tiers, of one side, each group by its noun, e.g. "parts a, b; tier t"."""
    groups = []
    for noun in ("part", "tier"):
        found = [name for kind, _, name in (entry.partition(" ") for entry in names) if kind == noun]
        if found:
            groups.append(f"{noun}{'s' if len(found) > 1 else ''} {_named(found)}")
    return "; ".join(groups)


def _named(names: Sequence[str]) -> str:
    """Up to NAMED names, then how many more there are."""
    return ", ".join(names[:NAMED]) + (f" and {len(names) - NAMED} more" if len(names) > NAMED else "")


def compared_document(origin: Origin | Resemblance) -> dict[str, Any] | None:
    """The profile compared with, as both JSON documents hold it under compared_with; None when nothing is compared."""
    if origin.bundled or origin.compared is None:
        return None
    return {"profile": origin.compared, "chosen_by": origin.chosen_by, "match": origin.match, "low": origin.low,
            "counts": {kind: [comparable, every] for kind, comparable, every in origin.counts},
            "only_here": list(origin.only_here), "only_there": list(origin.only_there),
            "elsewhere": list(origin.elsewhere),
            "higher": None if origin.higher is None else {"profile": origin.higher[0], "match": origin.higher[1]},
            "looser": [{"key": item.key, "part": item.part, "what": item.what, "sentence": item.sentence}
                       for item in origin.looser]}
```

In `check_lines`, replace its docstring

```python
    """What `profile check` found, as text: a section per check, then how the profile differs from the bundled one it
    is based on, and the verdict."""
```

with:

```python
    """What `profile check` found, as text: a section per check, then the match with the profile it is compared with
    and how it differs from it, and the verdict."""
```

replace `    lines = [f"checking {reviewed.location} ({origin_words(reviewed.resemblance)})", *_section("loads", (), "ok"),`
with `    lines = [f"checking {reviewed.location} ({_origin_words(reviewed.resemblance)})", *_section("loads", (), "ok"),`,
and replace `    return [*lines, *_compared(reviewed.resemblance),` with
`    return [*lines, *_match_lines(reviewed.resemblance), *_compared(reviewed.resemblance),`.

In `check_document`, replace:

```python
    resemblance = reviewed.resemblance
    compared = None
    if not resemblance.bundled and resemblance.compared is not None:
        compared = {"profile": resemblance.compared,
                    "looser": [{"key": i.key, "part": i.part, "what": i.what,
                                "sentence": i.sentence} for i in resemblance.looser]}
    problems = [*((EXAMPLES, text) for text in reviewed.examples), *((CHECKS, text) for text in own.problems),
                *((EVALS, text) for text in own.evals)]
    return _check_document(checked.ok, reviewed.location, problems, reviewed.files, own.checks, compared)
```

with:

```python
    problems = [*((EXAMPLES, text) for text in reviewed.examples), *((CHECKS, text) for text in own.problems),
                *((EVALS, text) for text in own.evals)]
    return _check_document(checked.ok, reviewed.location, problems, reviewed.files, own.checks,
                           compared_document(reviewed.resemblance))
```

- [ ] **Step 4: Write the failing `check` report tests**

In `tests/cli/reports/test_report.py`, add `from dataclasses import replace` after `import json`. In
`test_a_part_without_the_litmus_its_base_gives_it_is_said_under_the_profile_and_again_under_strict` replace:

```python
    origin = Origin("mine.yaml", False, "cli", looser=(Loosened("litmus", "cli", "", said),))
    assert lines(state=EnforcementView(strict=(FindingView("litmus", said),)), origin=origin, strict=True) == [
        "OK: no violations", "enforcement", "  profile:     mine.yaml (custom; closest bundled: cli)",
```

with:

```python
    origin = Origin("mine.yaml", False, "cli", looser=(Loosened("litmus", "cli", "", said),), chosen_by="based_on",
                    match=0.8)
    assert lines(state=EnforcementView(strict=(FindingView("litmus", said),)), origin=origin, strict=True) == [
        "OK: no violations", "enforcement", "  profile:     mine.yaml (custom; compared with cli, based_on; match 80%)",
```

and replace the whole test `test_a_profile_file_below_the_working_folder_is_named_from_it` with:

```python
COUNTS = (("parts", 4, 5), ("part_keys", 7, 7), ("tiers", 0, 0), ("guards", 1, 1), ("profile", 1, 1))
"""The counts of a profile with one part of its own besides four it shares."""


def closest(location: str, **changes) -> Origin:
    """A custom profile at location compared with web, the bundled profile of highest match, at 81% with COUNTS; the
    fields given replaced."""
    return replace(Origin(location, False, "web", chosen_by="closest", match=0.81, counts=COUNTS), **changes)


def test_a_profile_file_below_the_working_folder_is_named_from_it():
    assert lines(origin=closest("/src/arch/mine.yaml"))[:3] == [
        "OK: no violations", "enforcement", "  profile:     arch/mine.yaml (custom; compared with web, closest; match 81%)"]
    assert lines(origin=closest("/elsewhere/mine.yaml"))[2] == (
        "  profile:     /elsewhere/mine.yaml (custom; compared with web, closest; match 81%)")


def test_a_low_match_is_said_under_the_profile_line_with_why_and_one_that_is_not_low_only_in_it():
    low = closest("/src/mine.yaml", match=0.73, low=True, guards_off=("no-comments",))
    assert lines(origin=low)[2:5] == [
        "  profile:     mine.yaml (custom; compared with web, closest; match 73%)",
        "    match:       73%, low: 27% of what check reads under either profile has nothing to compare with in the "
        "other, so the list below says little about how check would do under web",
        "    guards off:  no-comments"]
    assert lines(origin=closest("/src/mine.yaml"))[2:] == [
        "  profile:     mine.yaml (custom; compared with web, closest; match 81%)"]


def test_the_json_document_holds_the_profile_compared_with_under_compared_with_and_no_closest_key():
    origin = closest("mine.yaml", only_here=("part jobs",))
    profile = json.loads(json_document("mine.yaml", origin, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert list(profile) == ["location", "bundled", "compared_with", "guards_off", "baseline_off", "looser"]
    assert profile["compared_with"] == {
        "profile": "web", "chosen_by": "closest", "match": 0.81, "low": False,
        "counts": {"parts": [4, 5], "part_keys": [7, 7], "tiers": [0, 0], "guards": [1, 1], "profile": [1, 1]},
        "only_here": ["part jobs"], "only_there": [], "elsewhere": [], "higher": None, "looser": []}
    bundled = json.loads(json_document("web", Origin("web"), AppChecked((), EnforcementView(), {}, True), False))
    assert bundled["enforcement"]["profile"]["compared_with"] is None
    assert "closest" not in bundled["enforcement"]["profile"]
```

- [ ] **Step 5: Run them to see them fail**

Run: `timeout 120 uv run pytest -q tests/cli/reports/test_report.py`
Expected: FAIL: the profile line reads `(custom; closest bundled: web)`, no `match:` line, and the JSON key is
`closest`.

- [ ] **Step 6: The enforcement section says the match**

In `xarch/cli/reports/report.py` replace `from xarch.cli.reports.profile_report import origin_words` with
`from xarch.cli.reports.profile_report import compared_document, compared_words, low_reason, percent`; in
`_enforcement_lines` replace:

```python
    lines = ["enforcement", _line("profile", f"{shown(Path(origin.location), cwd)} ({origin_words(origin)})", 2)]
```

with:

```python
    lines = ["enforcement", _line("profile", f"{shown(Path(origin.location), cwd)} ({compared_words(origin)})", 2)]
    if origin.low:
        lines.append(_line("match", f"{percent(origin.match)}, low: {low_reason(origin)}", 4))
```

and in `_enforcement_document` replace:

```python
        "profile": {"location": origin.location, "bundled": origin.bundled, "closest": origin.compared,
```

with:

```python
        "profile": {"location": origin.location, "bundled": origin.bundled, "compared_with": compared_document(origin),
```

- [ ] **Step 7: Run the report tests to see them pass**

Run: `timeout 120 uv run pytest -q tests/cli/reports`
Expected: all pass.

- [ ] **Step 8: The bootstrap tests follow, and pin the gate's number**

In `tests/bootstrap/test_check_enforcement.py`:

```bash
sed -i 's/(custom; closest bundled: web)/(custom; compared with web, closest; match 100%)/' tests/bootstrap/test_check_enforcement.py
sed -i 's/"profile": {"location": "web", "bundled": True, "closest": None,/"profile": {"location": "web", "bundled": True, "compared_with": None,/' tests/bootstrap/test_check_enforcement.py
grep -c "compared with web, closest; match 100%" tests/bootstrap/test_check_enforcement.py
```

Expected: `5`. (Each of those profiles is `web.yaml` with a guard dropped, a key added on a paired part or a folder
excluded, all comparable, so 100%.) Then in `test_a_custom_copy_of_a_bundled_profile_is_compared_with_it`, after its
last line (`    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-comments"]`)
add:

```python
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert "closest" not in profile
    compared = profile["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["match"], compared["low"]) == ("web", "closest", 1.0, False)
    assert compared["looser"] == profile["looser"]
```

In `tests/bootstrap/test_profile_check.py`:

- replace `import json\n\nimport pytest` with `import json\nfrom pathlib import Path\n\nimport pytest`;
- after `COPY = "architecture/mine/mine.yaml"` add:

```python
XARCH = Path(__file__).parents[2] / "architecture.yaml"
"""xarch's own profile, based on cli."""
```

- replace `    assert result.output.splitlines()[0] == f"checking {COPY} (custom; closest bundled: web)"` with
  `    assert result.output.splitlines()[0] == f"checking {COPY} (custom; based_on: web)"` (the copy `profile new`
  writes says `based_on: web`);
- just before `def test_an_unknown_key_fails_with_the_keys_that_exist(tmp_path):` add:

```python
def test_xarch_s_own_profile_is_compared_with_cli_the_profile_it_is_based_on_and_matches_it_at_80_percent():
    result = runner.invoke(app, ["profile", "check", str(XARCH)])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking {XARCH} (custom; based_on: cli)"
    assert lines[4:6] == [
        "  match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, "
        "9 of 9 profile keys sit where both profiles have them",
        "    only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering"]
    assert lines[6].startswith("  compared: looser than cli")
    compared = json.loads(runner.invoke(app, ["profile", "check", str(XARCH), "--format", "json"]).output)["compared_with"]
    assert {key: compared[key] for key in ("profile", "chosen_by", "match", "low", "counts", "higher")} == {
        "profile": "cli", "chosen_by": "based_on", "match": 0.8, "low": False,
        "counts": {"parts": [12, 15], "part_keys": [72, 91], "tiers": [21, 31], "guards": [11, 11], "profile": [9, 9]},
        "higher": None}


```

- in `test_each_public_name_a_copy_accepts_as_only_the_tests_is_a_way_it_is_looser` replace:

```python
    assert json.loads(result.output)["compared_with"] == {"profile": "web", "looser": [
        {"key": "known", "part": "", "what": "kernel/ids.py:make",
         "sentence": "the tests-only check accepts kernel/ids.py:make as a name only the tests use (guards.dead-code.known)"}]}
```

  with:

```python
    compared = json.loads(result.output)["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["match"]) == ("web", "based_on", 1.0)
    assert compared["looser"] == [
        {"key": "known", "part": "", "what": "kernel/ids.py:make",
         "sentence": "the tests-only check accepts kernel/ids.py:make as a name only the tests use (guards.dead-code.known)"}]
```

- in `test_json_gives_ok_the_problems_by_check_the_files_and_the_difference` replace
  `    assert good["compared_with"] == {"profile": "web", "looser": []}` with:

```python
    assert good["compared_with"] == {
        "profile": "web", "chosen_by": "based_on", "match": 1.0, "low": False,
        "counts": {"parts": [12, 12], "part_keys": [69, 69], "tiers": [17, 17], "guards": [11, 11], "profile": [6, 6]},
        "only_here": [], "only_there": [], "elsewhere": [], "higher": None, "looser": []}
```

- [ ] **Step 9: Run them to see them pass**

Run: `timeout 600 uv run pytest -q tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py tests/cli`
Expected: all pass.

Run: `uv run ruff check && uv run xarch check >/dev/null; echo "exit $?" && uv run xarch check --strict >/dev/null; echo "exit $?"`
Expected: `All checks passed!`, `exit 0`, `exit 0` (a `weak: ... origin_words is public, but no other file of the app
names it` means Step 3's rename to `_origin_words` was missed).

- [ ] **Step 10: Commit**

```bash
git add xarch/cli/reports/profile_report.py xarch/cli/reports/report.py tests/cli/reports/test_profile_report.py \
  tests/cli/reports/test_report.py tests/bootstrap/test_profile_check.py tests/bootstrap/test_check_enforcement.py
git commit -m "profile check prints the match with the profile it is compared with, its counts by kind, the parts and tiers that pair with nothing, the parts of the same name at another path, why a low one says little and the bundled profile that matches higher; check's enforcement line names the profile, why and the match, with a match line when it is low; both JSON documents hold the same compared_with, and check's enforcement.profile.closest is gone

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: README, CHANGELOG, the golden docs and the gates

**Files:**
- Modify: `README.md:235-242` (the `profile check` paragraph), `:361` (JSON sample), `:420` (text sample),
  `:436-447` (the `profile` bullet)
- Modify: `CHANGELOG.md` (`[Unreleased]`, `### Added` at line 8 and `### Changed` at line 60)
- Regenerated, expected unchanged: `docs/cli/**`, `docs/web/**`, `docs/xarch/**`

**Interfaces:**
- Consumes: the output of Tasks 2-4 as the docs describe it.
- Produces: nothing code reads.

- [ ] **Step 1: README**

Apply these four exact replacements in `README.md` (each old text occurs once):

Old (`:235-242`):

```
to its examples, and shows how it differs from the bundled profile it is based on, as information (but for a part
left without the litmus the bundled profile gives it, which fails `check --strict`). With no argument it checks the
project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen; `--format
json` gives `{"ok", "profile", "problems": [{"check", "message"}], "files", "checks", "compared_with"}`, `check`
being `load`, `examples`, `checks` (a check of the profile's own) or `evals` (an eval of its own), `files`
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load.
```

New:

```
to its examples, and shows how it differs from the bundled profile it is compared with, as information (but for a part
left without the litmus the bundled profile gives it, which fails `check --strict`). Before that comparison a `match:`
line says how much the two profiles have in common: `match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part
keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them`, then the parts
and tiers only one of them has, each part the other has by the same name at another path, `low: ...` when the match
is below 75%, and the bundled profile that matches higher than the one `based_on` names. With no argument it checks
the project's configured profile. Exit 0 when valid, 1 when it has problems, 2 when no profile can be chosen;
`--format json` gives `{"ok", "profile", "problems": [{"check", "message"}], "files", "checks", "compared_with"}`,
`check` being `load`, `examples`, `checks` (a check of the profile's own) or `evals` (an eval of its own), `files`
being how many files the profile points to and `checks` how many checks it writes itself, made or not; both are
`null` for a profile that does not load. `compared_with` is `null` for a bundled profile or one no bundled profile
resembles, else `{"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there", "elsewhere", "higher",
"looser"}`: `chosen_by` `based_on` or `closest`, `match` the share to two decimals (`0.8`), `counts` `{"parts",
"part_keys", "tiers", "guards", "profile"}` each `[comparable, all]`, and `higher` `null` or `{"profile", "match"}`.
```

Old (`:361`): `    "profile": {"location": "web", "bundled": true, "closest": null, "guards_off": [], "baseline_off": [],`
New: `    "profile": {"location": "web", "bundled": true, "compared_with": null, "guards_off": [], "baseline_off": [],`

Old (`:420`): `  profile:     arch/mine.yaml (custom; closest bundled: web)`
New: `  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)`

Old (`:436-437`):

```
- `profile`: the bundled name, or the custom file's path and the bundled profile it is based on or, failing that,
  most resembles (the first by name on a tie); one sharing no part resembles none, and nothing is compared. `guards off` lists
```

New:

```
- `profile`: the bundled name, or the custom file's path, the bundled profile it is compared with, why (`based_on`,
  the one its `based_on` names, else `closest`, the one of highest match, the first by name on a tie) and the match:
  the share of what `check` reads under either profile (each part, each key a part, a tier or the profile writes, each
  guard switched on) that has a counterpart in the other. Parts pair by name, then by layout path, and tiers by name,
  then by subject; a part or tier that pairs with none has no counterpart, nor does any key it holds. A match below
  75% is low and says so on a `match:` line under this one, with why; `profile check` shows the counts. One no part
  pairs with is no candidate, and with none left nothing is compared. In JSON, `enforcement.profile.compared_with`
  holds the same object as `profile check`'s (`null` when nothing is compared). `guards off` lists
```

Old (`:439-440`):

```
  line names that key. For a custom file, each way it is looser than the one it resembles, compared only where both use the same
  name: a target
```

New:

```
  line names that key. For a custom file, each way it is looser than the one it is compared with, compared only on
  the parts and tiers that pair (a part renamed in place is still compared, under its own name): a target
```

Old (`:445-447`, the end of the same bullet):

```
  other's, an entry of `review.never` or `review.mask` the other holds and this one drops. A profile that says `based_on: <bundled name>` is compared with that one, else with the one sharing the
  most part names.
```

New:

```
  other's, an entry of `review.never` or `review.mask` the other holds and this one drops.
```

Then: `grep -n "closest\|--against\|most part names" README.md`
Expected: three lines, each `closest` as a `chosen_by` value (the `profile check` paragraph's "`based_on` or
`closest`", the sample `(custom; compared with web, closest; match 100%)`, and "else `closest`, the one of highest
match"); no `--against` (5.3), no "most part names".

- [ ] **Step 2: CHANGELOG**

In `CHANGELOG.md`, directly under `## [Unreleased]` / `### Added` (line 8, before the first `- The kinds `records`...`
entry) add:

```
- The match of a custom profile with the bundled one it is compared with: the share of what `check` reads under
  either profile (each part, each key a part, a tier or the profile writes, each setting of a kind of `holds` on its
  own, each guard switched on, each check of the profile's own of an id both write) that has a counterpart in the
  other. A match below 75% is low and says why. It is printed on every run that compares: `profile check` says
  `match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, ...`, the parts and tiers only one profile has,
  the parts of the same name at another path, and the bundled profile that matches higher than the one `based_on`
  names; `check`'s enforcement section names the match on its `profile:` line, `(custom; compared with cli, based_on;
  match 80%)`, with a `match:` line under it when it is low. `compared_with` in the JSON of both gains `chosen_by`,
  `match`, `low`, `counts`, `only_here`, `only_there`, `elsewhere` and `higher`.
```

and directly under the `### Changed` of `[Unreleased]` (line 60, before its first entry) add:

```
- Without `based_on`, a custom profile is compared with the bundled profile of highest match (the first by name on a
  tie, and one no part pairs with never), no longer the one sharing the most part names. Parts pair by name, then by
  layout path, and tiers by name, then by subject, and the ways a profile is looser are compared on the parts and
  tiers that pair, so a part renamed in place is still compared, under its own name. `profile check` heads a profile
  `custom; based_on: cli` or `custom; closest bundled: cli, match 80%`.
- `check --format json`: `enforcement.profile.closest` is now `enforcement.profile.compared_with`, the same object as
  `profile check`'s `compared_with` (`null` when nothing is compared).
```

- [ ] **Step 3: Regenerate the golden docs and see an empty diff**

```bash
uv run python - <<'EOF'
from pathlib import Path
from xarch.bootstrap.wiring import build_controllers
spec = build_controllers().spec
for profile, out in (("cli", "docs/cli"), ("web", "docs/web"), ("architecture.yaml", "docs/xarch")):
    for found in spec.docs(profile).files:
        Path(out, *found.path).write_text(found.template, encoding="utf-8")
EOF
git status --short docs/ && git diff --stat docs/
```

Expected: no output beyond the untracked spec and plan under `docs/superpowers/` (this step changes no profile and no
template). A changed file under `docs/cli`, `docs/web` or `docs/xarch` is a behaviour change: restore it with
`git checkout -- <file>` and find its cause.

- [ ] **Step 4: The corpora are untouched**

Run: `git diff --stat b829b84 -- tests/bootstrap/corpora tests/bootstrap/test_recorded_corpora.py docs/examples`
Expected: no output.

- [ ] **Step 5: Run every gate**

Run the suite in the background (about four minutes):

```bash
timeout 900 uv run pytest -q -p no:cacheprovider 2>&1 | tail -3
```

Expected: `... passed`, no failures.

Then:

```bash
uv run ruff check
uv run xarch check >/dev/null; echo "exit $?"
uv run xarch check --strict >/dev/null; echo "exit $?"
uv run xarch profile check architecture.yaml; echo "exit $?"
```

Expected: `All checks passed!`, `exit 0`, `exit 0`, and `profile check` prints:

```
checking architecture.yaml (custom; based_on: cli)
  loads: ok
  files: all 23 it points to are present
  examples: ok: they import only what their part may
  match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, 9 of 9 profile keys sit where both profiles have them
    only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering
  compared: looser than cli (information; a part left without the litmus it gives fails `check --strict`):
```

followed by the same 18 sentence lines as before this step and `OK: the profile is valid`, `exit 0`. Compare the
comparison and the verdict with Task 1 Step 1's record (today's lines 5-24 are the new lines 7-26):

```bash
uv run xarch profile check architecture.yaml > /tmp/5-1-profile-check-after.txt
diff <(sed -n '5,$p' /tmp/5-1-profile-check-before.txt) <(sed -n '7,$p' /tmp/5-1-profile-check-after.txt) && echo SAME
diff <(sed -n '2,4p' /tmp/5-1-profile-check-before.txt) <(sed -n '2,4p' /tmp/5-1-profile-check-after.txt) && echo SAME
```

Expected: `SAME` twice. If the number is not 80%, stop: report the printed number with each row of the spec's §2 table
before and after (Task 2 Step 8's script prints them); do not change an item rule.

- [ ] **Step 6: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "README and CHANGELOG say the match: what it counts, low below 75%, printed by profile check and check, the bundled profile of highest match without based_on, parts paired by name then path, and check's enforcement.profile.compared_with in place of closest; the golden docs regenerate unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.**
- §1 items 1-5: the match (Task 2), printed on every comparing run in text and JSON (Task 4), low below 75% with the
  reason (Tasks 2, 4), the highest match without `based_on`, lowest name on a tie, no candidate with no paired part
  (Task 2), pairing by name then path and tiers by name then subject (Task 2), looser over the pairing (Task 3),
  `closest` → `compared_with` in `check`'s JSON (Task 4). `based_on` wins over a higher match (Task 2 test 13);
  `--strict` is untouched (no task edits `baseline_off` or the litmus rule; Task 4 Step 9 runs `check --strict`).
- §2 items: `_items`, `_part_keys`, `_tier_keys`, `_profile_keys` follow the lists one for one (`imports.may` a
  non-empty row; `imports.libraries` when `imports_libraries` lists the part; `imports.must`; one per
  `imports_types_only` target; `uses.never`; one per `holds` kind plus one per `names`/`immutable`/`built_by`;
  `untested`, `litmus`, `shared`, `entry`, `package_only`; tier, subject entries held by tier and part, the six tier
  keys with `imports.may` not None; guards by `KEY`; `libraries`, `testing.skips`, reserved, files, excluded, fakes,
  checks). Left-out keys are not read. Pairing, comparability, the union counted once, the exact fraction, `counts`
  order, `only_here`/`only_there` by name, `elsewhere` in this profile's order: Task 2 (`_paired_parts`,
  `_paired_tiers`, `_counted`, `_counts`, `_share`, `_unpaired`, `_elsewhere`). The table: Task 2 Step 8.
- §3: `origin_of` in Task 2 (bundled unchanged; `based_on` even with no part paired, low; highest match else; none →
  uncompared; `higher` only when strictly higher, lowest name on a tie).
- §4: Task 1 (`Origin`, `Resemblance`, the adapter, docstrings); `LOW` public in `looseness.py` (Task 2).
- §5: Task 3, with the module docstring.
- §6: Task 4 (header words, match lines, `only` grouping with five and `and N more`, `same name, other path`, the low
  lines, `higher`, the enforcement line and its `match:` low line, both JSON documents through `compared_document`).
- §7: Task 5 (README four places, CHANGELOG Added and Changed, `enforcement.py:21` in Task 1, `profile_report.py:193`
  docstring in Task 4, golden docs regenerated).
- §8 edges: based_on sharing no part (Task 2 test 14), no candidate (test 11), tie (test 12), two parts at one path
  (`_paired_parts` takes other's first unpaired in its order; each pairs once), `()` vs `None` (test 9), `_sentence`
  unchanged.
- §9 tests 1-17: Task 2 holds 1, 5-17 (test 15 split in two: exactly 75% and just below in one test, the rounding case
  in its own), Task 3 holds 2-4. Service, report and bootstrap tiers: Tasks 2 and 4. Rename-only edits: Task 1.
- §10 gates: Task 5 Step 5.

**Placeholder scan.** No TBD, no "similar to"; every code step carries its code.

**Type consistency.** `_paired_parts(mine, other) -> dict[str, str]`, `_paired_tiers(mine, other, parts) ->
dict[str, str]`, `_into(target, parts) -> Target` are defined in Task 2 and used under the same names in Task 3.
`counts` is `tuple[tuple[str, int, int], ...]` in `Origin`, `Resemblance`, `_counts`, the reports and every test.
`compared_words`, `percent`, `low_reason`, `compared_document` are defined in `profile_report.py` and imported by
`report.py` under those names in the same task.

**Review Focus.** Each of its five lines has its test in the owning task, named there.
<!-- task-pipeline: validated -->
