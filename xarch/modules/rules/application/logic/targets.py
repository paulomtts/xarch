"""What a fact a rule reads is compared with: the kinds of target of rules as data, a closed list, and whether a fact
is a finding under the rule's quantifier. Under MAY_NOT a fact is one when it matches a target, and its hit is the
target it matches; under MAY_ONLY when it matches none.

    existing   every fact matches: a rule under MAY_NOT whose kept facts are findings by being there
    packages   the first step of what an import names is one of the words
    names      the dotted path a fact names is one of the names, or lies below it, the first such name its hit; a
               method called matches a name written `.<method>()` (held as ("", "<method>()")), the last such
    private    the name an import takes is private in the language of the app
    parts      the place an import or a call reaches lies in one of the parts the words name
    places     the place an import into the app reaches is one a place the file's part may import reaches, the
               name it takes included
    allowance  the place a test's import into the app reaches is one that what the test's subject may import
               reaches, from the instance the test mirrors (see tier_of)
    test-code  a test file's import into the tests' package is of test code it may import: the fakes when its
               tier tests a part they stand in for, any other file that is no test file in its own folder
"""
from __future__ import annotations

from collections.abc import Callable

from xarch.kernel.logic.placement import reaches
from xarch.modules.rules.application.logic.tier_of import Tested, allowance, as_place, may_use_fakes
from xarch.modules.rules.domain.rule import MAY_NOT, MAY_ONLY, Facts, Found, Targets
from xarch.modules.rules.domain.values import Profile

Matcher = Callable[[Targets, Found, Facts, Profile], tuple[str, ...] | None]
"""How a fact is matched against targets: the target it matches, None when it matches none."""


def finding(quantifier: str, hit: tuple[str, ...] | None) -> bool:
    """Whether a fact that matched hit (None: nothing) is a finding under the quantifier."""
    if quantifier == MAY_NOT:
        return hit is not None
    if quantifier == MAY_ONLY:
        return hit is None
    raise ValueError(f"no quantifier is named {quantifier!r}: use {MAY_NOT} or {MAY_ONLY}")


def matcher(kind: str) -> Matcher:
    """How a fact is matched against targets of a kind, by the kind's name."""
    found = _KINDS.get(kind)
    if found is None:
        raise ValueError(f"no kind of target is named {kind!r}")
    return found


def _existing(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    return ()


def _packages(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    path = found.fact.path
    return path[:1] if path and path[0] in targets.words else None


def _names(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact = found.fact
    if fact.kind == "method":
        return next((n for n in reversed(targets.names) if len(n) == 2 and not n[0]
                     and n[1].removesuffix("()") == fact.name), None)
    path = fact.path
    for name in targets.names:
        if path[:len(name)] == name:
            return name
    return None


def _private(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    name = found.fact.name
    return (name,) if name is not None and profile.language.is_private(name) else None


def _parts(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact = found.fact
    return fact.target if fact.at is not None and fact.at.part in targets.words else None


def _places(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    src, fact = found.read.place, found.fact
    return fact.target if src is not None and fact.at is not None and any(
        reaches(t, src, fact.at, fact.name) for t in targets.places) else None


def _allowance(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    read, fact = found.read, found.fact
    tier = next(t for t in profile.tiers if t.name == read.tier)
    allowed = allowance(profile, Tested(tier, read.instance, read.own, read.is_test, read.is_fake, read.mirrors))
    return fact.target if fact.at is not None and any(
        reaches(t, as_place(read.instance), fact.at) for t in allowed) else None


def _test_code(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    read, target = found.read, found.fact.target
    if profile.fakes is not None and target[:len(profile.fakes.folder)] == profile.fakes.folder:
        return target if may_use_fakes(profile, next(t for t in profile.tiers if t.name == read.tier)) else None
    if target in facts.test_files:
        return None
    return target if read.own and target[:len(read.own)] == read.own else None


_KINDS = {"existing": _existing, "packages": _packages, "names": _names, "private": _private, "parts": _parts,
          "places": _places, "allowance": _allowance, "test-code": _test_code}
"""How a fact is matched against each kind of target, by its name."""
