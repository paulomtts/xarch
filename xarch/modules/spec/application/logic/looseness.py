"""How a profile compares with the bundled ones: which it resembles, the guards it leaves off, and every way it is
looser than the one it resembles.

The closest bundled profile is the one a profile says it is based on, else the one sharing the most part names, the
first by name on a tie; one sharing none resembles no bundled profile. Looser is compared only where both have the
same name (a part, a tier, a file), and only in these ways, each one entry: a target added to a part's `may_import`
that no target of the bundled one covers (a target covers what lies below it: the same part and scope, its path a
start of the added one's, and no name pattern or the same one; so a name pattern added to a target, or a folder below
it, narrows it, and is not looser); an outside package added to a part's `libraries`, or `libraries` dropped as a
whole; a target added to a part's `must_import`, or the key dropped from a part that has it; a name the bundled
`forbidden` list of a part holds that no entry of the custom list covers (`time` covers `time.time`); a part newly
marked `untested`; a part dropped from a tier's `types_only`; a target added to a tier's `may_also_import` that no
target of the bundled tier's covers; a tier no longer `apply_forbidden`; a name dropped from `testing.skips`; a `files`
entry no longer `pinned`; a name the bundled profile `reserved` holds that the custom one does not; a part the bundled
profile gives a `litmus` that the custom one redefines without one. Anything stricter, and what is
compared in no way above (the layout, new parts, the guards' parameters, `fakes`), is not listed.
"""
from __future__ import annotations

from collections.abc import Mapping

from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import LITMUS, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture
from xarch.profile_values.placement import Target

Looser = tuple[str, str, str]
"""(key, part, what): one way a profile is looser, before it is said."""


def guards_off(architecture: Architecture) -> tuple[str, ...]:
    """The guards xarch has that the profile does not switch on, in xarch's order."""
    on = {KEY[type(guard)] for guard in architecture.guards}
    return tuple(name for name in ORDER if name not in on)


def closest(architecture: Architecture, bundled: Mapping[str, Architecture]) -> str | None:
    """The bundled profile the architecture says it is based on, else the one sharing the most part names."""
    if architecture.based_on in bundled:
        return architecture.based_on
    scores = {name: len(set(architecture.parts) & set(other.parts)) for name, other in bundled.items()}
    best = max(scores.values(), default=0)
    return min(name for name, score in scores.items() if score == best) if best else None


def looser(custom: Architecture, base: Architecture) -> list[Looser]:
    shared = [name for name in custom.parts if name in base.parts]
    found: list[Looser] = []
    for name in shared:
        before = base.rules.get(name, ())
        found += [("may_import", name, _shown(t)) for t in custom.rules.get(name, ())
                  if not any(_covers(b, t) for b in before)]
    if base.libraries is not None:
        if custom.libraries is None:
            found.append(("libraries", "", ""))
        else:
            found += [("libraries", name, package) for name in shared for package in custom.libraries.get(name, ())
                      if package not in base.libraries.get(name, ())]
    for name in shared:
        kept = custom.forbidden.get(name, ())
        found += [("forbidden", name, ".".join(banned)) for banned in base.forbidden.get(name, ())
                  if not any(banned[:len(entry)] == entry for entry in kept)]
    for name in shared:
        before, now = base.parts[name].must_import, custom.parts[name].must_import
        if before and not now:
            found.append(("must_import", name, ""))
        else:
            found += [("must_import", name, _shown(t)) for t in now if before and t not in before]
    found += [("untested", name, "") for name in shared if custom.parts[name].untested and not base.parts[name].untested]
    found += [(LITMUS, name, "") for name in shared if base.parts[name].litmus and not custom.parts[name].litmus]
    tiers = {tier.name: tier for tier in custom.tiers}
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None:
            found += [("types_only", tier.name, part) for part in tier.types_only if part not in mine.types_only]
            found += [("may_also_import", tier.name, _shown(t)) for t in mine.may_also_import
                      if not any(_covers(b, t) for b in tier.may_also_import)]
    found += [("apply_forbidden", tier.name, "") for tier in base.tiers
              if tier.forbidden and tier.name in tiers and not tiers[tier.name].forbidden]
    skips = custom.framework.skips if custom.framework is not None else ()
    if base.framework is not None:
        found += [("testing.skips", "", ".".join(name)) for name in base.framework.skips if name not in skips]
    files = {file.path: file for file in custom.files}
    found += [("files.pinned", "", "/".join(file.path)) for file in base.files
              if file.pinned and file.path in files and not files[file.path].pinned]
    found += [("reserved", "", name) for name in base.reserved if name not in custom.reserved]
    return found


def _covers(wider: Target, target: Target) -> bool:
    """Whether a target of the bundled profile allows everything the added one does."""
    if wider.part == EVERYTHING:
        return True
    return (wider.part == target.part and wider.scope == target.scope
            and target.sub[:len(wider.sub)] == wider.sub and wider.names in ("", target.names))


def origin_of(location: str, architecture: Architecture, bundled: bool,
              others: Mapping[str, Architecture]) -> Origin:
    """Where the architecture at location comes from: a bundled one is its own baseline; a custom one is compared with
    the closest of the others, the bundled architectures by name, and is looser than it in the ways it says."""
    off = guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    name = closest(architecture, others)
    if name is None:
        return Origin(location, False, None, off, (), ())
    baseline = guards_off(others[name])
    return Origin(location, False, name, off, tuple(g for g in off if g in baseline),
                  tuple(Loosened(key, part, what, sentence(key, part, what))
                        for key, part, what in looser(architecture, others[name])))


def sentence(key: str, part: str, what: str = "") -> str:
    """How one way a profile is looser is said, naming the key of the profile that says it."""
    match key:
        case "may_import":
            return f"{part} may also import {what} (parts.{part}.may_import)"
        case "libraries" if not part:
            return "outside packages are not checked"
        case "libraries" if what == EVERYTHING:
            return f"{part} may import any outside package (parts.{part}.libraries)"
        case "libraries":
            return f"{part} may also import {what} (parts.{part}.libraries)"
        case "forbidden":
            return f"{part} no longer forbids {what} (parts.{part}.forbidden)"
        case "must_import" if not what:
            return f"{part} no longer has to import anything (parts.{part}.must_import)"
        case "must_import":
            return f"{part} may also meet must_import with {what} (parts.{part}.must_import)"
        case "untested":
            return f"{part} is newly marked untested (parts.{part}.untested)"
        case "litmus":
            return f"{part} has no litmus, though the profile it is compared with gives it one (parts.{part}.litmus)"
        case "types_only":
            return f"the {part} tests may now call {what} (tiers.{part}.types_only)"
        case "may_also_import":
            return f"the {part} tests may also import {what} (tiers.{part}.may_also_import)"
        case "apply_forbidden":
            return f"the {part} tests are no longer held to their part's forbidden list (tiers.{part}.apply_forbidden)"
        case "testing.skips":
            return f"{what} is no longer counted as a skip (testing.skips)"
        case "files.pinned":
            return f"{what} is no longer pinned (files.{what}.pinned)"
        case "reserved":
            return f"{what} is no longer reserved (reserved.{what})"
    return " ".join(filter(None, (key, part, what)))


def _shown(target: Target) -> str:
    if target.part == EVERYTHING:
        return "everything"
    scope = f"@{target.scope}" if target.scope == "any" else ""
    names = f":{target.names}" if target.names else ""
    return target.part + scope + "".join(f"/{step}" for step in target.sub) + names
