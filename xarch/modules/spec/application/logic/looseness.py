"""How a profile compares with the bundled ones: which it resembles, the guards it leaves off, and every way it is
looser than the one it resembles.

The closest bundled profile is the one a profile says it is based on, else the one sharing the most part names, the
first by name on a tie; one sharing none resembles no bundled profile. Looser is compared only where both have the
same name (a part, a tier, a file), and only in these ways, each one entry: a target added to a part's `may_import`
(a name pattern added to a target narrows it, and is not looser); an
outside package added to a part's `libraries`, or `libraries` dropped as a whole; a target added to a part's
`must_import`, or the key dropped from a part that has it; a name the bundled `forbidden` list of a part holds that no
entry of the custom list covers (`time` covers `time.time`); a part newly marked `untested`; a part dropped from a
tier's `types_only`; a tier no longer `apply_forbidden`; a name dropped from `testing.skips`; a `files` entry no longer
`pinned`. Anything stricter, and what is compared in no way above (the layout, new parts, the guards' parameters,
`fakes`), is not listed.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from xarch.kernel.logic.placement import EVERYTHING, Target
from xarch.modules.spec.application.logic.guard_names import guard_name
from xarch.modules.spec.domain.guards import GUARDS
from xarch.modules.spec.domain.values import Architecture

Loosening = tuple[str, str, str]
"""(key, part, what), as Loosened holds them."""


def guards_off(architecture: Architecture) -> tuple[str, ...]:
    """The guards xarch has that the profile does not switch on, in xarch's order."""
    on = {guard_name(guard) for guard in architecture.guards}
    return tuple(name for name in GUARDS if name not in on)


def closest(architecture: Architecture, bundled: Mapping[str, Architecture]) -> str | None:
    """The bundled profile the architecture says it is based on, else the one sharing the most part names."""
    if architecture.based_on in bundled:
        return architecture.based_on
    scores = {name: len(set(architecture.parts) & set(other.parts)) for name, other in bundled.items()}
    best = max(scores.values(), default=0)
    return min(name for name, score in scores.items() if score == best) if best else None


def looser(custom: Architecture, base: Architecture) -> list[Loosening]:
    shared = [name for name in custom.parts if name in base.parts]
    found: list[Loosening] = []
    for name in shared:
        before = base.rules.get(name, ())
        found += [("may_import", name, _shown(t)) for t in custom.rules.get(name, ())
                  if t not in before and replace(t, names="") not in before]
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
    tiers = {tier.name: tier for tier in custom.tiers}
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None:
            found += [("types_only", tier.name, part) for part in tier.types_only if part not in mine.types_only]
    found += [("apply_forbidden", tier.name, "") for tier in base.tiers
              if tier.forbidden and tier.name in tiers and not tiers[tier.name].forbidden]
    skips = custom.framework.skips if custom.framework is not None else ()
    if base.framework is not None:
        found += [("testing.skips", "", ".".join(name)) for name in base.framework.skips if name not in skips]
    files = {file.path: file for file in custom.files}
    found += [("files.pinned", "", "/".join(file.path)) for file in base.files
              if file.pinned and file.path in files and not files[file.path].pinned]
    return found


def _shown(target: Target) -> str:
    if target.part == EVERYTHING:
        return "everything"
    scope = f"@{target.scope}" if target.scope == "any" else ""
    names = f":{target.names}" if target.names else ""
    return target.part + scope + "".join(f"/{step}" for step in target.sub) + names
