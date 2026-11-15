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

from xarch.kernel.logic.placement import reaches
from xarch.modules.rules.application.logic.tier_of import Tested, allowance, as_place, may_use_fakes
from xarch.modules.rules.domain.rule import MAY_NOT, MAY_ONLY, Facts, Found, Targets
from xarch.modules.rules.domain.values import Profile


def compared(quantifier: str, targets: Targets, found: Found, facts: Facts,
             profile: Profile) -> tuple[bool, tuple[str, ...] | None]:
    """Whether the fact is a finding, and the target it matched (None: none)."""
    hit = matched(targets, found, facts, profile)
    match quantifier:
        case "may_not":
            return hit is not None, hit
        case "may_only":
            return hit is None, None
    raise ValueError(f"no quantifier is named {quantifier!r}: use {MAY_NOT} or {MAY_ONLY}")


def matched(targets: Targets, found: Found, facts: Facts, profile: Profile) -> tuple[str, ...] | None:
    fact, read = found.fact, found.read
    match targets.kind:
        case "existing":
            return ()
        case "packages":
            return fact.path[:1] if fact.path[:1] and fact.path[0] in targets.words else None
        case "names":
            if fact.kind == "method":
                return next((n for n in reversed(targets.names) if len(n) == 2 and not n[0]
                             and n[1].removesuffix("()") == fact.name), None)
            return next((n for n in targets.names if fact.path[:len(n)] == n), None)
        case "private":
            return (fact.name,) if fact.name is not None and profile.language.is_private(fact.name) else None
        case "parts":
            return fact.target if fact.at is not None and fact.at.part in targets.words else None
        case "places":
            src, at = read.place, fact.at
            return fact.target if src is not None and at is not None and any(
                reaches(t, src, at, fact.name) for t in targets.places) else None
        case "allowance":
            tier = next(t for t in profile.tiers if t.name == read.tier)
            allowed = allowance(profile, Tested(tier, read.instance, read.own, read.is_test, read.is_fake, read.mirrors))
            return fact.target if fact.at is not None and any(
                reaches(t, as_place(read.instance), fact.at) for t in allowed) else None
        case "test-code":
            tier = next(t for t in profile.tiers if t.name == read.tier)
            if profile.fakes is not None and fact.target[:len(profile.fakes.folder)] == profile.fakes.folder:
                return fact.target if may_use_fakes(profile, tier) else None
            if fact.target in facts.test_files:
                return None
            return fact.target if read.own and fact.target[:len(read.own)] == read.own else None
    raise ValueError(f"no kind of target is named {targets.kind!r}")
