"""How a profile compares with the bundled ones: which it resembles, the guards it leaves off, and every way it is
looser than the one it resembles.

The closest bundled profile is the one a profile says it is based on, else the one sharing the most part names, the
first by name on a tie; one sharing none resembles no bundled profile. Looser is compared only where both have the
same name (a part, a tier, a file), and only in these ways, each one entry: a target added to a part's `imports.may`
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

from collections.abc import Mapping

from xarch.kernel.logic.names import outside_text
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.guards import KEY, ORDER
from xarch.modules.spec.domain.published import LINE, LITMUS, Loosened, Origin
from xarch.modules.spec.domain.values import Architecture, DeadCode, NoTwins
from xarch.profile_values.placement import Target

Looser = tuple[str, str, str]
"""(key, part, what): one way a profile is looser, before it is said."""
LOOSER = ("imports.may", "imports.may.types_only", "imports.libraries", "uses.never", "imports.must", "untested",
          LITMUS, "imports.types_only", "imports.also", "uses.apply_never", "testing.skips", "files.pinned", "reserved",
          "known", "translated", "review.never", "review.mask", "evals.placement.lines")
"""Every key a way a profile is looser is listed under, each said by a sentence of its own."""


def _guards_off(architecture: Architecture) -> tuple[str, ...]:
    """The guards xarch has that the profile does not switch on, in xarch's order."""
    on = {KEY[type(guard)] for guard in architecture.guards}
    return tuple(name for name in ORDER if name not in on)


def _closest(architecture: Architecture, bundled: Mapping[str, Architecture]) -> str | None:
    """The bundled profile the architecture says it is based on, else the one sharing the most part names."""
    if architecture.based_on in bundled:
        return architecture.based_on
    scores = {name: len(set(architecture.parts) & set(other.parts)) for name, other in bundled.items()}
    best = max(scores.values(), default=0)
    return min(name for name, score in scores.items() if score == best) if best else None


def _looser(custom: Architecture, base: Architecture) -> list[Looser]:
    member = custom.language.checked.member
    shared = [name for name in custom.parts if name in base.parts]
    found: list[Looser] = []
    for name in shared:
        before = base.rules.get(name, ())
        found += [("imports.may", name, _shown(t)) for t in custom.rules.get(name, ())
                  if not any(_covers(b, t) for b in before)]
    for name in shared:
        allows, marks = custom.rules.get(name, ()), custom.parts[name].types_only
        found += [("imports.may.types_only", name, _shown(t)) for t in base.parts[name].types_only
                  if any(_covers(c, t) for c in allows) and not any(_covers(c, t) for c in marks)]
    if base.libraries is not None:
        if custom.libraries is None:
            found.append(("imports.libraries", "", ""))
        else:
            found += [("imports.libraries", name, package) for name in shared for package in custom.libraries.get(name, ())
                      if package not in base.libraries.get(name, ())]
    for name in shared:
        kept = custom.uses_never.get(name, ())
        found += [("uses.never", name, outside_text(banned, member)) for banned in base.uses_never.get(name, ())
                  if not any(banned[:len(entry)] == entry for entry in kept)]
    for name in shared:
        before, now = base.parts[name].must_import, custom.parts[name].must_import
        if before and not now:
            found.append(("imports.must", name, ""))
        else:
            found += [("imports.must", name, _shown(t)) for t in now if before and t not in before]
    found += [("untested", name, "") for name in shared if custom.parts[name].untested and not base.parts[name].untested]
    found += [(LITMUS, name, "") for name in shared if base.parts[name].litmus and not custom.parts[name].litmus]
    tiers = {tier.name: tier for tier in custom.tiers}
    for tier in base.tiers:
        mine = tiers.get(tier.name)
        if mine is not None:
            found += [("imports.types_only", tier.name, part) for part in tier.types_only
                      if part not in mine.types_only]
            found += [("imports.also", tier.name, _shown(t)) for t in mine.may_also_import
                      if not any(_covers(b, t) for b in tier.may_also_import)]
    found += [("uses.apply_never", tier.name, "") for tier in base.tiers
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
    found += [("translated", part, "") for part in _translators(custom) if part not in translators]
    found += [("review.never", "", path) for path in base.never if path not in custom.never]
    found += [("review.mask", "", text) for text in base.mask if text not in custom.mask]
    found += [("evals.placement.lines", name, f"{custom.lines.get(name, LINE):.2f}") for name in shared
              if custom.lines.get(name, LINE) < base.lines.get(name, LINE)]
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
    the closest of the others, the bundled architectures by name, and is looser than it in the ways it says."""
    off = _guards_off(architecture)
    if bundled:
        return Origin(location, True, None, off, off, ())
    name = _closest(architecture, others)
    if name is None:
        return Origin(location, False, None, off, (), ())
    baseline = _guards_off(others[name])
    return Origin(location, False, name, off, tuple(g for g in off if g in baseline),
                  tuple(Loosened(key, part, what, _sentence(key, part, what))
                        for key, part, what in _looser(architecture, others[name])))


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
