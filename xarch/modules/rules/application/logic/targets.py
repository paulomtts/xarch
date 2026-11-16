"""What a fact a rule reads is compared with: the kinds of target of rules as data (see the vocabulary for what each
means), and whether a fact is a finding under the rule's quantifier. A fact is compared with each target of its rule
in turn, and the first it matches is its hit; under MAY_NOT a fact is a finding when it matches one, under MAY_ONLY
when it matches none. A kind of target that does not apply to a fact's kind matches no fact of it.
"""
from __future__ import annotations

from collections.abc import Callable

from xarch.kernel.logic.placement import name_matches, reaches
from xarch.modules.rules.application.logic.places import targets_of
from xarch.modules.rules.application.logic.tier_of import Tested, allowance, as_place, may_use_fakes
from xarch.modules.rules.domain.rule import MAY_NOT, MAY_ONLY, Facts, Found, Match
from xarch.modules.rules.domain.values import Profile

Matcher = Callable[[Match, Found, Facts, Profile], tuple[str, ...] | None]
"""How a fact is matched against a target: what it matched, None when it matches none."""


def finding(quantifier: str, hit: tuple[str, ...] | None) -> bool:
    """Whether a fact that matched hit (None: nothing) is a finding under the quantifier."""
    if quantifier == MAY_NOT:
        return hit is not None
    if quantifier == MAY_ONLY:
        return hit is None
    raise ValueError(f"no quantifier is named {quantifier!r}: use {MAY_NOT} or {MAY_ONLY}")


def matched(targets: tuple[Match, ...], found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    """What the fact matched of the targets, the first it matches; None when it matches none."""
    for match in targets:
        hit = _KINDS[match.kind](match, found, facts, profile)
        if hit is not None:
            return hit
    return None


def _exist(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    return ()


def _path(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact = found.fact
    if fact.kind == "method-call":
        return next((n for n in reversed(match.names) if len(n) == 2 and not n[0]
                     and n[1].removesuffix("()") == fact.name), None)
    if not fact.path:
        return None
    return next((name for name in match.names if fact.path[:len(name)] == name), None)


def _package(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    path = found.fact.path
    return path[:1] if path and path[0] in match.words else None


def _name(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    name = found.fact.name
    if name is None:
        return None
    return next(((p,) for p in match.words if name_matches(p, name)), None)


def _text(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    text = found.fact.text
    return next(((p,) for p in match.words if name_matches(p, text)), None) if text else None


def _part(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact = found.fact
    return fact.target if fact.at is not None and fact.at.part in match.words else None


def _place(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    src, fact = found.read.place, found.fact
    return fact.target if src is not None and fact.at is not None and any(
        reaches(t, src, fact.at) for t in match.places) else None


def _permitted(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    read, fact = found.read, found.fact
    if fact.kind == "import-into-tests":
        return _test_code(found, facts, profile)
    if fact.at is None:
        return None
    if not read.test:
        src = read.place
        return fact.target if src is not None and src.part is not None and any(
            reaches(t, src, fact.at, fact.name) for t in targets_of(profile, src.part)) else None
    tier = next((t for t in profile.tiers if t.name == read.tier), None)
    if tier is None:
        return None
    allowed = allowance(profile, Tested(tier, read.instance, read.own, read.is_test, read.is_fake, read.mirrors))
    return fact.target if any(reaches(t, as_place(read.instance), fact.at) for t in allowed) else None


def _test_code(found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    read, target = found.read, found.fact.target
    if profile.fakes is not None and target[:len(profile.fakes.folder)] == profile.fakes.folder:
        tier = next((t for t in profile.tiers if t.name == read.tier), None)
        return target if tier is not None and may_use_fakes(profile, tier) else None
    if target in facts.test_files:
        return None
    return target if read.own and target[:len(read.own)] == read.own else None


def _outside(match: Match, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact = found.fact
    outside = ("relative" not in fact.traits and bool(fact.path) and fact.path[0] != facts.root
               and "standard" not in fact.traits)
    return fact.path if outside else None


_KINDS: dict[str, Matcher] = {"exist": _exist, "path": _path, "package": _package, "name": _name, "text": _text,
                              "part": _part, "place": _place, "permitted": _permitted, "outside": _outside}
"""How a fact is matched against each kind of target, by its name."""

NAMES = tuple(_KINDS)
"""The name of every kind of target the engine matches."""
