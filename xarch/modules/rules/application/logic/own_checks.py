"""The checks a profile writes itself, as spec reads them from the format (see profile_values' checks), made into
rules: each target is resolved by its kind of the vocabulary (a place by the target grammar, against the parts of the
profile and the part the check's scope names; a dotted name into its steps; any other value as written), and a part
it names must be a part of the profile. A check that names a word the vocabulary does not hold, or one that does not
apply, a place or a part the profile does not have, or a fact the language's reader does not supply, is refused with
every problem of every check at once (ChecksRefused). A check that reads a fact the reader supplies only partly is
listed as approximate.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from xarch.kernel.logic.capabilities import shortfalls
from xarch.kernel.logic.targets import target
from xarch.modules.rules.domain.errors import ChecksRefused, RuleRefused
from xarch.modules.rules.domain.rule import EXISTING, MUST_BE_REACHED, MUST_REACH, Match, OwnCheck, Rule
from xarch.modules.rules.domain.values import Profile
from xarch.modules.rules.domain.vocabulary import NAMES, PLACES, TARGETS
from xarch.profile_values.capabilities import FACTS, Shortfall
from xarch.profile_values.checks import WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage

PART = "part"
"""The kind of target whose values are parts of the profile."""


def resolved(profile: Profile) -> Profile:
    """The profile with the checks it writes itself made into rules, and those that read a fact the language supplies
    only partly added to its approximate keys; raises ChecksRefused with every problem when one cannot be made."""
    checks = own(profile.written, profile)
    return replace(profile, checks=checks, approximate=(*profile.approximate, *approximate(checks, profile.language)))


def own(written: Mapping[str, WrittenCheck], profile: Profile) -> tuple[OwnCheck, ...]:
    """Each check as a rule with its examples, in the profile's order."""
    found: list[OwnCheck] = []
    problems: list[str] = []
    for name, check in written.items():
        count = len(problems)
        targets = _targets(name, check, profile, problems)
        if len(problems) != count:
            continue
        try:
            rule = _rule_of(name, check, targets)
        except RuleRefused as refused:
            problems += [f"checks.{name}.{problem}" for problem in refused.problems]
            continue
        problems += supplied(name, rule, profile.language)
        found.append(OwnCheck(rule, check.flagged, check.clean))
    if problems:
        raise ChecksRefused(tuple(problems))
    return tuple(found)


def _rule_of(name: str, check: WrittenCheck, targets: tuple[Match, ...]) -> Rule:
    """The rule a check means, its targets resolved; raises RuleRefused when a word does not exist or apply."""
    quantified = check.quantified
    return Rule(name, check.within, check.read, quantified.slot,
                EXISTING if quantified.slot == MUST_BE_REACHED else targets, check.sayings, keep=check.keep,
                exempt=check.exempt, mode=check.mode, key=f"checks.{name}", links=quantified.through,
                via=quantified.through_only, roots=quantified.start, spread=quantified.then_through,
                elsewhere=quantified.by_another_file)


def supplied(name: str, rule: Rule, language: CheckedLanguage) -> list[str]:
    """A problem for each fact the rule needs that the language's reader does not supply."""
    if language.supplies is None:
        return []
    supplies = {s.fact: s for s in language.supplies}
    return [f"checks.{name}: needs {short.fact} ({FACTS[short.fact]}), which the reader of {language.title} does "
            "not supply: read another kind of fact, or drop the check"
            for short in shortfalls(rule.key, rule.needs, supplies) if short.note is None]


def approximate(checks: tuple[OwnCheck, ...], language: CheckedLanguage) -> tuple[Shortfall, ...]:
    """The checks that read a fact the language's reader supplies only partly, by the fact."""
    supplies = {s.fact: s for s in language.supplies or ()}
    return tuple(short for check in checks for short in shortfalls(check.rule.key, check.rule.needs, supplies)
                 if short.note is not None)


def _targets(name: str, check: WrittenCheck, profile: Profile, problems: list[str]) -> tuple[Match, ...]:
    slot = check.quantified.slot
    where = f"checks.{name}.{slot}" + (".targets" if slot == MUST_REACH else "")
    part = check.within.named_part
    owner = (part, profile.parts[part]) if part in profile.parts else None
    return tuple(match for written in check.quantified.targets
                 if (match := _match(written, owner, profile, where, problems)) is not None)


def _match(written: WrittenTarget, owner: tuple[str, tuple[str, ...]] | None, profile: Profile, where: str,
           problems: list[str]) -> Match | None:
    kind, values = written.kind, written.values
    form = next((k.values for k in TARGETS if k.name == kind), "")
    if form == PLACES:
        count = len(problems)
        places = tuple(t for v in values
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems)) is not None)
        return Match(kind, places=places) if len(problems) == count else None
    if kind == PART:
        missing = [v for v in values if v not in profile.parts]
        if missing:
            problems.append(f"{where}.part: no part named {', '.join(map(repr, missing))}")
            return None
    if form == NAMES:
        return Match(kind, names=tuple(("", value[1:]) if value.startswith(".") else tuple(value.split("."))
                                       for value in values))
    return Match(kind, words=values)
