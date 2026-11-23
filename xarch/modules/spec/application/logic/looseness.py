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
from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import replace
from fractions import Fraction

from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import BASED_ON, CLOSEST, LINE, LITMUS, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture, DeadCode, NoTwins, PackageOnly, Part, Tier
from xarch.profile_values.placement import Target

Looser = tuple[str, str, str]
"""(key, part, what): one way a profile is looser, before it is said."""
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "imports.types_only", "imports.also", "uses.apply_never", "testing.skips", "files.pinned", "reserved",
          "known", "translated", "review.never", "review.mask", "evals.placement.lines")
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
        case "litmus":
            return f"{part} has no litmus, though the profile it is compared with gives it one (parts.{part}.litmus)"
        case "imports.types_only":
            return f"the {part} tests may now call {what} (tiers.{part}.imports.types_only)"
        case "imports.also":
            return f"the {part} tests may also import {what} (tiers.{part}.imports.also)"
        case "uses.apply_never":
            return f"the {part} tests are no longer held to their part's never list (tiers.{part}.uses.apply_never)"
        case "testing.skips":
            return f"{what} is no longer counted as a skip (testing.skips)"
        case "files.pinned":
            return f"{what} is no longer pinned (files.{what}.pinned)"
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


def _shown(target: Target) -> str:
    if target.part == EVERYTHING:
        return "everything"
    scope = f"@{target.scope}" if target.scope == "any" else ""
    names = f":{target.names}" if target.names else ""
    return target.part + scope + "".join(f"/{step}" for step in target.sub) + names
