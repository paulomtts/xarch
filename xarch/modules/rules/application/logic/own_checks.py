"""The checks a profile writes itself, as spec reads them from the format (see profile_values' checks), made into
rules: each target is resolved by its kind of the vocabulary (a place by the target grammar, against the parts of the
profile and the part the check's scope names; a dotted name into its steps; any other value as written), and a part
it names must be a part of the profile. A check that names a word the vocabulary does not hold, or one that does not
apply, a place or a part the profile does not have, or a fact the language's reader does not supply, is not made: its
problems are listed, and the others are made all the same (made); to run, every check must be made, else they are
refused with every problem of every check at once (ChecksRefused). A check that reads a fact the reader supplies only
partly is listed as approximate.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from xarch.kernel.logic.capabilities import shortfalls
from xarch.kernel.logic.examples import is_test_example
from xarch.kernel.logic.names import outside_steps
from xarch.kernel.logic.targets import outside_imports, target
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.errors import ChecksRefused, RuleRefused
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import (
    COUNTS,
    EXISTING,
    FILE_REACH,
    MUST_BE_REACHED,
    MadeChecks,
    Match,
    OwnCheck,
    Rule,
)
from xarch.modules.rules.domain.vocabulary import NAMES, PARTS, PLACES, TARGETS
from xarch.profile_values.capabilities import FACTS, Shortfall
from xarch.profile_values.checks import WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage


def resolved(profile: Profile) -> Profile:
    """The profile with the checks it writes itself made into rules, and those that read a fact the language supplies
    only partly added to its approximate keys; raises ChecksRefused with every problem when one cannot be made."""
    checks = _own(profile.written, profile)
    return replace(profile, checks=checks, approximate=(*profile.approximate, *_approximate(checks, profile.language)))


def _own(written: Mapping[str, WrittenCheck], profile: Profile) -> tuple[OwnCheck, ...]:
    """Each check as a rule with its examples, in the profile's order; raises ChecksRefused with every problem when
    one cannot be made."""
    found = made(written, profile)
    if found.problems:
        raise ChecksRefused(found.problems)
    return found.checks


def made(written: Mapping[str, WrittenCheck], profile: Profile) -> MadeChecks:
    """Each check that can be made as a rule with its examples, and every problem of each that cannot, both in the
    profile's order."""
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
        lacking = unsupplied(f"checks.{name}", rule, profile.language, "check")
        named = rule.naming("accepted", tuple(dict.fromkeys(variable for entry in check.accepted
                                                            for variable, _ in entry.by)))
        problems += [*lacking, *(f"checks.{name}.{problem}" for problem in named)]
        if not lacking and not named:
            found.append(OwnCheck(rule, check.flagged, check.clean))
    return MadeChecks(tuple(found), tuple(problems))


def _rule_of(name: str, check: WrittenCheck, targets: tuple[Match, ...]) -> Rule:
    """The rule a check means, its targets resolved; raises RuleRefused when a word does not exist or apply."""
    quantified = check.quantified
    return Rule(name, check.within, check.read, quantified.slot,
                EXISTING if quantified.slot in (MUST_BE_REACHED, *COUNTS) else targets, check.sayings, keep=check.keep,
                exempt=check.exempt, mode=check.mode, key=f"checks.{name}", links=quantified.through,
                via=quantified.through_only, roots=quantified.start, spread=quantified.then_through,
                elsewhere=quantified.by_another_file, count=quantified.count)


def unsupplied(address: str, rule: Rule, language: CheckedLanguage, what: str) -> list[str]:
    """A problem at address for each fact the rule needs that the language's reader does not supply at all, its fix
    to drop what the rule is made of (the check, the eval); none when the language's data file does not say what its
    reader supplies. A fact supplied partly is no problem."""
    if language.supplies is None:
        return []
    supplies = {s.fact: s for s in language.supplies}
    return [f"{address}: needs {short.fact} ({FACTS[short.fact]}), which the reader of {language.title} does not "
            f"supply: read another kind of fact, or drop the {what}"
            for short in shortfalls(rule.key, rule.needs, supplies) if short.note is None]


def _approximate(checks: tuple[OwnCheck, ...], language: CheckedLanguage) -> tuple[Shortfall, ...]:
    """The checks that read a fact the language's reader supplies only partly, by the fact."""
    supplies = {s.fact: s for s in language.supplies or ()}
    return tuple(short for check in checks for short in shortfalls(check.rule.key, check.rule.needs, supplies)
                 if short.note is not None)


def _targets(name: str, check: WrittenCheck, profile: Profile, problems: list[str]) -> tuple[Match, ...]:
    slot = check.quantified.slot
    where = f"checks.{name}.{slot}" + (".targets" if slot in FILE_REACH else "")
    part = check.within.named_part
    owner = (part, profile.parts[part]) if part in profile.parts else None
    return tuple(match for written in check.quantified.targets
                 if (match := _match(written, owner, profile, where, problems)) is not None)


def _match(written: WrittenTarget, owner: tuple[str, tuple[str, ...]] | None, profile: Profile, where: str,
           problems: list[str]) -> Match | None:
    kind, values = written.kind, written.values or ()
    form = next((k.values for k in TARGETS if k.name == kind), "")
    if form == PLACES:
        count = len(problems)
        places = tuple(t for v in values
                       if (t := target(v, owner, profile.parts, profile.parts, f"{where}.place", problems,
                                       alone="a check that names no part", repeats=profile.repeats,
                                       place=True)) is not None)
        return Match(kind, places=places) if len(problems) == count else None
    if form == PARTS:
        words = [repeat.word for repeat in profile.repeats]
        told = [(v, outside_imports(v, profile.parts, words)) for v in values]
        prefixed = [said for _, said in told if said is not None]
        problems += [f"{where}.part: {said}" for said in prefixed]
        missing = [v for v, said in told if v not in profile.parts and said is None]
        if missing:
            problems.append(f"{where}.part: no part named {', '.join(map(repr, missing))}")
        if prefixed or missing:
            return None
    if form == NAMES:
        return Match(kind, names=tuple(("", value[1:]) if value.startswith(".") else outside_steps(value, profile.language.member)
                                       for value in values))
    return Match(kind, words=values)


def placed(path: str, app: str, tests: str) -> tuple[tuple[str, ...], tuple[str, ...], bool]:
    """Where a file of a check's example sits, by its path below the folder holding the app, written with "/": how it
    is shown, its steps below its root (the app folder, or the folder of the tests, which a test's path starts with),
    and whether it is test code."""
    steps = tuple(path.split("/"))
    if is_test_example(steps, tests):
        return steps, steps[1:], True
    return (app, *steps), steps, False


def held_problems(check_id: str, flagged: list[Violation | Weak], clean: list[Violation | Weak]) -> list[str]:
    """What is wrong with how a check of the profile's own holds to its examples, each problem at its address: it must
    find something in its flagged code (what it found there), and nothing in its clean code."""
    where = f"checks.{check_id}.examples"
    found = [] if flagged else [f"{where}.flagged: the check finds nothing in it: make the code hold what the check "
                                "is written to find, or correct the check"]
    if clean:
        first = clean[0]
        found.append(f"{where}.clean: the check finds {len(clean)} in it, the first {first.file}:{first.line}: "
                     f"{first.message}: make the code clean, or correct the check")
    return found
