"""How a profile compares with the bundled ones: the one it is compared with, how much the two have in common (its
match), the guards it leaves off, and every way it is looser than that one.

A custom profile is compared with the bundled profile its `based_on` names, else with the one of highest match, the
first by name on a tie; one no part pairs with is no candidate, and with none left nothing is compared. For one run,
`--against` names the profile compared with instead, bundled or a file, and then a bundled profile is compared too, even
with one no part pairs with, and no other is said to match higher. The match is the share of the items of either
profile, one per thing `check` reads, that have a counterpart in the other: each part; each key of a part that holds a
value (imports.may, imports.libraries, imports.must, each target marked types_only, uses.never, each kind of holds and
each setting it writes, untested, litmus, shared, entry, package_only, optional, imports.accepted); each tier, each
entry of its subject and each of its keys that holds a value; each guard switched on; and each key of the profile as a
whole (libraries, testing.skips, each reserved module, files entry and excluded folder, fakes, each check of its own).
Parts pair by name, then by the same layout path; tiers by name, then by the same subject, its parts read through the
pairing; each at most once. An item has a counterpart when every part and tier holding it pairs (a check of the
profile's own, when the other writes one of its id), so a key one side drops on a paired holder still has one. A match
below LOW, or one with no part paired, is low.

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
marked `untested`; a part newly `optional`; an entry of a part's `imports.accepted` (a file, and what it imports)
the bundled part does not hold; a part dropped from a tier's `imports.types_only`; a target added to
a tier's `imports.also` that no
target of the bundled tier's covers; a tier no longer `uses.apply_never`; a name dropped from `testing.skips`; a `files`
entry no longer `pinned`; a name the bundled profile `reserved` holds that the custom one does not; a part the bundled
profile gives a `litmus` that the custom one redefines without one; a public name `guards.dead-code.known` accepts as
only the tests' that the bundled profile's does not; a part `guards.no-twins.translated` lists that the bundled
profile's does not; a path `review.never` holds back, or a text `review.mask` hides, in the bundled profile that the
custom one does not write (each compared as written: it sends more); a part whose line under `evals.placement.lines`
is below the one the bundled profile gives it (written, else LINE: it flags less); a kind a part's `holds` allows that
the bundled part's does not (no `holds` allows every kind, and `classes` allows `records` and `exceptions` too); a
setting of a kind dropped or widened, compared for each kind either part lists and both allow, on the settings each
holds the kind to (those written under it, else for `records` and `exceptions` those under `classes`, `immutable`
never for an exception): `names` dropped, or a pattern added that no bundled pattern matches read as a name,
`immutable` dropped, `built_by` dropped or a part added to it; a part's `shared` dropped or lowered; a tier's
`imports.must` dropped, or a part added to it; a tier no longer `plain_tables`; `testing.beside` set where the bundled
profile leaves it out; an entry of `testing.shared` the bundled profile does not share; a tier `fakes.tiers` lists
that the bundled profile's does not; an entry of a check's `accepted` (a file, and the variables it names) that the
bundled profile's check of the same id does not hold; an entry of `structure.accepted` (a path) the bundled profile
does not hold. Anything stricter, and what is compared in no way above (the layout, new parts,
the guards' other parameters, `fakes`), is not listed.

A custom profile whose `based_on` is the path of a profile file is compared with that file, called by its path as
written, and is handed the files of its chain in order: that one, the one it names in turn, and so on; no file of the
chain is a candidate for the bundled profile of higher match. `--strict` then rests on the anchor: the bundled profile
the last file says it is based on, else the one of highest match with it, else none. A guard left off is excused only
when the anchor and every file of the chain leave it off too, and a part with no litmus that pairs with a part the
anchor gives one is listed under `litmus` too, after the ways it is looser than the file, unless that comparison lists
it already.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import replace
from fractions import Fraction

from xarch.kernel.logic.names import outside_text
from xarch.kernel.logic.placement import name_matches
from xarch.kernel.logic.targets import written_target
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic.holds_written import NARROWER
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import AGAINST, BASED_ON, CLOSEST, KINDS, LINE, LITMUS, Held, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture, DeadCode, NoTwins, PackageOnly, Part, Tier
from xarch.profile_values.checks import AcceptedFinding
from xarch.profile_values.placement import Target

Looser = tuple[str, str, str]
"""(key, part, what): one way a profile is looser, before it is said."""
HELD = ("holds.classes.names", "holds.classes.immutable", "holds.classes.built_by", "holds.functions.names",
        "holds.records.names", "holds.records.immutable", "holds.exceptions.names")
"""The key of each setting of a kind of holds, a way it is looser listed under, kind by kind in the order of KINDS."""
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          "optional", "imports.accepted", LITMUS, "holds", *HELD, "shared", "imports.types_only", "imports.also", "uses.apply_never",
          "tiers.imports.must", "plain_tables", "testing.skips", "testing.beside", "testing.shared", "fakes.tiers",
          "files.pinned", "reserved", "known", "checks.accepted", "structure.accepted",
          "translated", "review.never", "review.mask", "evals.placement.lines")
"""Every key a way a profile is looser is listed under, each said by a sentence of its own."""
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


def _guards_off(architecture: Architecture) -> tuple[str, ...]:
    """The guards xarch has that the profile does not switch on, in xarch's order."""
    on = {KEY[type(guard)] for guard in architecture.guards}
    return tuple(name for name in ORDER if name not in on)


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
               "entry": part.entry, "package_only": packaged, "optional": part.optional,
               "imports.accepted": bool(part.imports_accepted)}
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


def _here(target: Target, words: Mapping[str, str]) -> Target:
    """A target of the bundled profile renamed into the custom one, its own instance the part itself (scope none) when
    the part lies in no repeating folder of the custom profile (words), where it has no instance of its own."""
    return replace(target, scope="none") if target.scope == "own" and target.part not in words else target


def _looser(custom: Architecture, base: Architecture) -> list[Looser]:
    member = custom.language.checked.member
    words = custom.words()
    pairs = _paired_parts(custom, base)
    back = {theirs: name for name, theirs in pairs.items()}
    shared = [name for name in custom.parts if name in pairs]
    found: list[Looser] = []
    for name in shared:
        before = base.rules.get(pairs[name], ())
        found += [("imports.may", name, _shown(t, words)) for t in custom.rules.get(name, ())
                  if not any(_covers(b, _into(t, pairs)) for b in before)]
    for name in shared:
        allows = [_into(c, pairs) for c in custom.rules.get(name, ())]
        marks = [_into(c, pairs) for c in custom.parts[name].imports_types_only]
        found += [("imports.may.types_only", name, _shown(_here(_into(t, back), words), words))
                  for t in base.parts[pairs[name]].imports_types_only
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
            found += [("imports.must", name, _shown(t, words)) for t in now if before and _into(t, pairs) not in before]
    found += [("untested", name, "") for name in shared
              if custom.parts[name].untested and not base.parts[pairs[name]].untested]
    found += [("optional", name, "") for name in shared
              if custom.parts[name].optional and not base.parts[pairs[name]].optional]
    for name in shared:
        before = {(entry.file, entry.written) for entry in base.parts[pairs[name]].imports_accepted}
        found += [("imports.accepted", name, f"{'/'.join(entry.file)}: {entry.written}")
                  for entry in custom.parts[name].imports_accepted if (entry.file, entry.written) not in before]
    found += [(LITMUS, name, "") for name in shared if base.parts[pairs[name]].litmus and not custom.parts[name].litmus]
    found += [("holds", name, kind) for name in shared for kind in _allowed(custom.parts[name])
              if kind not in _allowed(base.parts[pairs[name]])]
    for name in shared:
        found += _settings_looser(custom.parts[name], base.parts[pairs[name]], pairs)
    for name in shared:
        before, now = base.parts[pairs[name]].shared, custom.parts[name].shared
        if before is not None and (now is None or now < before):
            found.append(("shared", name, "" if now is None else str(now)))
    paired = _paired_tiers(custom, base, pairs)
    tiers = {paired[tier.name]: tier for tier in custom.tiers if tier.name in paired}
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None:
            marked = {pairs.get(part, part) for part in mine.imports_types_only}
            found += [("imports.types_only", mine.name, back.get(part, part)) for part in tier.imports_types_only
                      if part not in marked]
            found += [("imports.also", mine.name, _shown(t, words)) for t in mine.imports_also
                      if not any(_covers(b, _into(t, pairs)) for b in tier.imports_also)]
    found += [("uses.apply_never", tiers[tier.name].name, "") for tier in base.tiers
              if tier.apply_never and tier.name in tiers and not tiers[tier.name].apply_never]
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None and tier.imports_must:
            found += _added("tiers.imports.must", mine.name, tier.imports_must, mine.imports_must, pairs)
    found += [("plain_tables", tiers[tier.name].name, "") for tier in base.tiers
              if tier.plain_tables and tier.name in tiers and not tiers[tier.name].plain_tables]
    skips = custom.framework.skips if custom.framework is not None else ()
    if base.framework is not None:
        found += [("testing.skips", "", outside_text(name, member)) for name in base.framework.skips if name not in skips]
    if custom.framework is not None and custom.framework.beside and not (base.framework is not None
                                                                         and base.framework.beside):
        found.append(("testing.beside", "", ""))
    if custom.framework is not None:
        before = base.framework.shared if base.framework is not None else ()
        found += [("testing.shared", "", "/".join(entry)) for entry in custom.framework.shared if entry not in before]
    if custom.fakes is not None:
        opened = base.fakes.tiers if base.fakes is not None else ()
        found += [("fakes.tiers", tier, "") for tier in custom.fakes.tiers if tier not in opened]
    files = {file.path: file for file in custom.files}
    found += [("files.pinned", "", "/".join(file.path)) for file in base.files
              if file.pinned and file.path in files and not files[file.path].pinned]
    found += [("reserved", "", name) for name in base.reserved if name not in custom.reserved]
    accepted = _known(base)
    found += [("known", "", entry) for entry in _known(custom) if entry not in accepted]
    held = {entry.path for entry in base.structure_accepted}
    found += [("structure.accepted", "", "/".join(entry.path)) for entry in custom.structure_accepted
              if entry.path not in held]
    for name, check in custom.checks.items():
        held = {(entry.file, entry.by) for entry in base.checks[name].accepted} if name in base.checks else set()
        found += [("checks.accepted", "", f"{name}: {_finding(entry)}") for entry in check.accepted
                  if (entry.file, entry.by) not in held]
    translators = _translators(base)
    found += [("translated", part, "") for part in _translators(custom) if pairs.get(part, part) not in translators]
    found += [("review.never", "", path) for path in base.never if path not in custom.never]
    found += [("review.mask", "", text) for text in base.mask if text not in custom.mask]
    found += [("evals.placement.lines", name, f"{custom.lines.get(name, LINE):.2f}") for name in shared
              if custom.lines.get(name, LINE) < base.lines.get(pairs[name], LINE)]
    return found


def _finding(entry: AcceptedFinding) -> str:
    """A finding an entry of a check's `accepted` names, as said: its file, then the variables it names it by."""
    named = " and ".join(f"{variable} {said}" for variable, said in entry.by)
    return f"{'/'.join(entry.file)}{f' with {named}' if named else ''}"


def _allowed(part: Part) -> tuple[str, ...]:
    """The kinds a part's holds allows, in the order of KINDS: every kind when it lists none, else those it lists and,
    when it lists classes, the kinds every class covers too."""
    listed = {held.kind for held in part.holds}
    if not listed:
        return KINDS
    return tuple(kind for kind in KINDS if kind in listed or ("classes" in listed and kind in NARROWER))


def _held_to(part: Part, kind: str) -> Held:
    """The settings a part holds a kind to: those written under it when the part lists it; else, for a kind every
    class covers, those written under classes when it lists classes (immutable never for an exception); else none."""
    held = {item.kind: item for item in part.holds}
    if kind in held:
        return held[kind]
    if kind in NARROWER and "classes" in held:
        wider = held["classes"]
        return Held(kind, wider.names, wider.immutable and kind != "exceptions")
    return Held(kind)


def _settings_looser(custom: Part, base: Part, pairs: Mapping[str, str]) -> list[Looser]:
    """Each setting of a kind the custom part drops or widens, against the base part it pairs with: compared for each
    kind either lists that both allow, on the settings each holds the kind to."""
    listed = {held.kind for held in (*custom.holds, *base.holds)}
    found: list[Looser] = []
    for kind in KINDS:
        if kind in listed and kind in _allowed(custom) and kind in _allowed(base):
            before, now = _held_to(base, kind), _held_to(custom, kind)
            if before.names and not now.names:
                found.append((f"holds.{kind}.names", custom.name, ""))
            elif before.names:
                found += [(f"holds.{kind}.names", custom.name, pattern) for pattern in now.names
                          if not any(name_matches(wider, pattern) for wider in before.names)]
            if before.immutable and not now.immutable:
                found.append((f"holds.{kind}.immutable", custom.name, ""))
            if before.built_by:
                found += _added(f"holds.{kind}.built_by", custom.name, before.built_by, now.built_by, pairs)
    return found


def _added(key: str, holder: str, before: tuple[str, ...], now: tuple[str, ...], pairs: Mapping[str, str]) -> list[Looser]:
    """A list of parts the base holder names, against the custom holder's: dropped, one entry; else each custom part,
    read through the pairing, the base does not name, said as written."""
    if not now:
        return [(key, holder, "")]
    return [(key, holder, name) for name in now if pairs.get(name, name) not in before]


def _known(architecture: Architecture) -> tuple[str, ...]:
    """The public names the architecture accepts as only the tests' (guards.dead-code.known)."""
    return next((guard.known for guard in architecture.guards if isinstance(guard, DeadCode)), ())


def _translators(architecture: Architecture) -> tuple[str, ...]:
    """The parts whose translations no-twins accepts (guards.no-twins.translated)."""
    return next((guard.translated for guard in architecture.guards if isinstance(guard, NoTwins)), ())


def _covers(wider: Target, target: Target) -> bool:
    """Whether a target of the bundled profile allows everything the added one does."""
    if wider.part == EVERYTHING:
        return True
    return (wider.part == target.part and wider.scope == target.scope
            and target.sub[:len(wider.sub)] == wider.sub and wider.names in ("", target.names))


def origin_of(location: str, architecture: Architecture, bundled: bool, others: Mapping[str, Architecture],
              against: str | None = None, chain: Sequence[Architecture] = ()) -> Origin:
    """Where the architecture at location comes from: a bundled one is its own baseline; a custom one is compared with
    the one of others, the bundled architectures by name, it says it is based on, else the one of highest match (the
    first by name on a tie, one no part pairs with never), and is looser than it in the ways it says. With chain, the
    profile files its based_on leads through when it is a path, in order, it is compared with the first, called by its
    based_on as written, which is never said to match higher, and --strict rests on the anchor (see _resting). With
    against, the name others holds the one profile --against names by, either is compared with that one alone, even
    when no part pairs, and no other is said to match higher."""
    if against is not None:
        return _compared(location, architecture, bundled, others[against], against, AGAINST, architecture.based_on)
    off = _guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    highest, best = _closest(architecture, others)
    if chain:
        name, chosen_by, base = architecture.based_on, BASED_ON, chain[0]
    elif architecture.based_on in others:
        name, chosen_by, base = architecture.based_on, BASED_ON, others[architecture.based_on]
    elif highest is not None:
        name, chosen_by, base = highest, CLOSEST, others[highest]
    else:
        return Origin(location, False, None, off, (), ())
    share = _share(_counts(architecture, base))
    origin = replace(_compared(location, architecture, False, base, name, chosen_by), anchor=name,
                     higher=(highest, round(float(best), 2)) if highest is not None and best > share else None)
    return _resting(origin, architecture, chain, others) if chain else origin


def _closest(architecture: Architecture, others: Mapping[str, Architecture]) -> tuple[str | None, Fraction]:
    """The one of others of highest match with the architecture, the first by name on a tie, one no part pairs with
    never, and that match; None and no match when none is left."""
    shares = {name: _share(_counts(architecture, other)) for name, other in others.items()
              if _paired_parts(architecture, other)}
    best = max(shares.values(), default=Fraction(0))
    return min((name for name, share in shares.items() if share == best), default=None), best


def _resting(origin: Origin, architecture: Architecture, chain: Sequence[Architecture],
             bundled: Mapping[str, Architecture]) -> Origin:
    """The origin of a profile compared with the profile file its based_on names, as --strict rests on its anchor:
    the bundled profile the last file of the chain says it is based on, else the one of highest match with that file.
    A guard left off is excused only when the anchor and every file of the chain leave it off too, none with no
    anchor; each part with no litmus that pairs with a part the anchor gives one, and that the comparison with the file
    does not list already, is listed after the ways it is looser than the file."""
    last = chain[-1]
    anchor = last.based_on if last.based_on in bundled else _closest(last, bundled)[0]
    if anchor is None:
        return replace(origin, baseline_off=(), anchor=None)
    base = bundled[anchor]
    excused = set(_guards_off(base)).intersection(*(_guards_off(file) for file in chain))
    listed = {item.part for item in origin.looser if item.key == LITMUS}
    pairs = _paired_parts(architecture, base)
    demanded = tuple(Loosened(LITMUS, name, anchor, _sentence(LITMUS, name, anchor))
                     for name, part in architecture.parts.items()
                     if not part.litmus and name in pairs and base.parts[pairs[name]].litmus and name not in listed)
    return replace(origin, baseline_off=tuple(g for g in origin.guards_off if g in excused),
                   looser=origin.looser + demanded, anchor=anchor)


def _compared(location: str, architecture: Architecture, bundled: bool, base: Architecture, name: str,
              chosen_by: str, based_on: str = "") -> Origin:
    """The architecture at location compared with base, which is called name: the guards both leave off, how it is
    looser, its match and its counts, and what pairs with nothing on either side."""
    off = _guards_off(architecture)
    counts = _counts(architecture, base)
    share = _share(counts)
    parts = _paired_parts(architecture, base)
    tiers = _paired_tiers(architecture, base, parts)
    looser = tuple(Loosened(key, part, what, _sentence(key, part, what)) for key, part, what in _looser(architecture, base))
    return Origin(location, bundled, name, off, tuple(g for g in off if g in _guards_off(base)), looser,
                  chosen_by=chosen_by, match=round(float(share), 2), low=share < LOW or not parts, counts=counts,
                  only_here=_unpaired(architecture, parts, tiers),
                  only_there=_unpaired(base, parts.values(), tiers.values()),
                  elsewhere=_elsewhere(architecture, base), based_on=based_on)


def _sentence(key: str, part: str, what: str = "") -> str:
    """How one way a profile is looser is said, naming the key of the profile that says it."""
    match key:
        case "imports.may":
            return f"{part} may also import {what} (parts.{part}.imports.may)"
        case "imports.may.types_only":
            return f"{part} may now call {what}, which it used only as a type (parts.{part}.imports.may.types_only)"
        case "imports.libraries" if not part:
            return "outside packages are not checked"
        case "imports.libraries" if what == EVERYTHING:
            return f"{part} may import any outside package (parts.{part}.imports.libraries)"
        case "imports.libraries":
            return f"{part} may also import {what} (parts.{part}.imports.libraries)"
        case "uses.never":
            return f"{part} no longer forbids {what} (parts.{part}.uses.never)"
        case "imports.must" if not what:
            return f"{part} no longer has to import anything (parts.{part}.imports.must)"
        case "imports.must":
            return f"{part} may also meet imports.must with {what} (parts.{part}.imports.must)"
        case "untested":
            return f"{part} is newly marked untested (parts.{part}.untested)"
        case "optional":
            return f"{part} is newly optional: structure no longer requires it (parts.{part}.optional)"
        case "imports.accepted":
            file, _, imported = what.partition(": ")
            return f"{part} accepts {file} importing {imported} (parts.{part}.imports.accepted)"
        case "litmus" if what:
            return (f"{part} has no litmus, though {what}, which --strict rests on, gives the part it pairs with one "
                    f"(parts.{part}.litmus)")
        case "litmus":
            return f"{part} has no litmus, though the profile it is compared with gives it one (parts.{part}.litmus)"
        case "holds":
            return f"{part} may also define {what} at the top level (parts.{part}.holds)"
        case _ if key.startswith("holds."):
            return _held_sentence(key, part, what)
        case "shared" if not what:
            return f"{part} is no longer held to be shared (parts.{part}.shared)"
        case "shared":
            return (f"the public names of {part} need only {what} users, fewer than the profile it is compared with asks "
                    f"(parts.{part}.shared)")
        case "imports.types_only":
            return f"the {part} tests may now call {what} (tiers.{part}.imports.types_only)"
        case "imports.also":
            return f"the {part} tests may also import {what} (tiers.{part}.imports.also)"
        case "uses.apply_never":
            return f"the {part} tests are no longer held to their part's never list (tiers.{part}.uses.apply_never)"
        case "tiers.imports.must" if not what:
            return f"the {part} tests no longer have to reach any part (tiers.{part}.imports.must)"
        case "tiers.imports.must":
            return f"the {part} tests may also meet imports.must by reaching {what} (tiers.{part}.imports.must)"
        case "plain_tables":
            return f"the table tests of the {part} tests may now branch (tiers.{part}.plain_tables)"
        case "testing.skips":
            return f"{what} is no longer counted as a skip (testing.skips)"
        case "testing.beside":
            return "tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)"
        case "testing.shared":
            return f"a test of any tier may also import the test code in {what} (testing.shared)"
        case "fakes.tiers":
            return f"the {part} tests may also import the fakes (fakes.tiers)"
        case "files.pinned":
            return f"{what} is no longer pinned (files.{what}.pinned)"
        case "structure.accepted":
            return f"the layout accepts the finding of {what} (structure.accepted)"
        case "checks.accepted":
            check, _, finding = what.partition(": ")
            return f"the check {check} accepts the findings of {finding} (checks.{check}.accepted)"
        case "known":
            return f"the tests-only check accepts {what} as a name only the tests use (guards.dead-code.known)"
        case "translated":
            return f"no-twins accepts each pair of classes a function of {part} translates (guards.no-twins.translated)"
        case "reserved":
            return f"{what} is no longer reserved (reserved.{what})"
        case "review.never":
            return f"{what} may be sent again: the profile it is compared with holds it back (review.never)"
        case "review.mask":
            return f"{what} is no longer masked before review sends (review.mask)"
        case "evals.placement.lines":
            return (f"{part} reads as doubtful only below {what}, a lower line than the profile it is compared with "
                    "gives it (evals.placement.lines)")
    raise ValueError(f"no sentence says how a profile is looser under {key!r}")


def _held_sentence(key: str, part: str, what: str) -> str:
    """How a setting of a kind of holds dropped or widened is said, at the address of the kind compared."""
    _, kind, setting = key.split(".")
    at = f"(parts.{part}.{key})"
    match setting:
        case "names" if not what:
            return f"the {kind} of {part} may be named anything {at}"
        case "names":
            return f"the {kind} of {part} may also be named {what} {at}"
        case "immutable":
            return f"the {kind} of {part} need no longer be immutable records {at}"
        case "built_by" if not what:
            return f"the {kind} of {part} may be built by any part {at}"
        case "built_by":
            return f"the {kind} of {part} may also be built by {what} {at}"
    raise ValueError(f"no sentence says how a profile is looser under {key!r}")


def _shown(target: Target, words: Mapping[str, str]) -> str:
    """How a target of the custom profile is said: `everything` as the word, any other as a reference (see
    written_target), the word that of the repeating folder its part lies in in the custom profile (words)."""
    return "everything" if target.part == EVERYTHING else written_target(target, words)
