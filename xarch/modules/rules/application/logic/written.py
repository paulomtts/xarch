"""A rule as the profile would write it as a check of its own (see profile_values' checks): what `xarch profile explain
<key> --rule` shows of a key's rules, so that a check xarch has reads as a check a profile could write. A rule written
so and read back is the same rule, its id and key aside: a check of one's own takes an id of its own, and its key is
`checks.<id>`. The text of it is the check format's.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from xarch.modules.rules.domain.rule import EXISTING, MUST_BE_REACHED, Match, OwnCheck, Rule
from xarch.profile_values.checks import Quantified, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Target

_IMPORT = re.compile(r"%import (?P<dotted>[^ %]+) (?P<name>[^ %]+)%")
"""The token of a line that imports a name from a file of the app, in the code of a check written for the
explanation."""


def written(rules: Iterable[Rule]) -> dict[str, WrittenCheck]:
    """The rules as checks of a profile, each under an id of its own (see ids)."""
    rules = list(rules)
    return {name: check_of(rule) for rule, name in zip(rules, ids(rules))}


def written_own(checks: Iterable[OwnCheck], language: CheckedLanguage) -> dict[str, WrittenCheck]:
    """Checks of a profile's own as its `checks` are written, each under its id with its examples, the tokens of the
    language (see filled) in their paths and code filled in."""
    return {own.rule.id: check_of(own.rule, _filled(own.flagged, language), _filled(own.clean, language))
            for own in checks}


def ids(rules: list[Rule]) -> list[str]:
    """An id for each rule written as a check: its own, then the part its scope names, then a number when two would
    be the same."""
    found: list[str] = []
    for rule in rules:
        base = f"{rule.id}-{rule.scope.named_part}" if rule.scope.named_part else rule.id
        name, count = base, 1
        while name in found:
            count += 1
            name = f"{base}-{count}"
        found.append(name)
    return found


def check_of(rule: Rule, flagged: tuple[tuple[str, str], ...] = (), clean: tuple[tuple[str, str], ...] = ()) -> WrittenCheck:
    """The rule as the check a profile would write, with the examples given."""
    targets = () if rule.quantifier == MUST_BE_REACHED else tuple(_target(match) for match in rule.targets)
    quantified = Quantified(rule.quantifier, targets, rule.links, rule.via, rule.roots, rule.spread, rule.elsewhere)
    return WrittenCheck(rule.facts, rule.scope, quantified, rule.sayings, rule.keep, rule.exempt, rule.mode, flagged,
                        clean)


def filled(text: str, language: CheckedLanguage) -> str:
    """The text with the tokens of the language filled in: `%extension%`, `%comment%`, and `%import <dotted> <name>%`,
    a line that imports name from the file of the app that dotted names, as the language's importing says
    (left as written when it does not say)."""
    text = text.replace("%extension%", language.extension).replace("%comment%", language.comment)
    if not language.importing:
        return text
    return _IMPORT.sub(lambda found: language.importing.format(dotted=found["dotted"], name=found["name"]), text)


def _filled(files: tuple[tuple[str, str], ...], language: CheckedLanguage) -> tuple[tuple[str, str], ...]:
    return tuple((filled(path, language), filled(code, language)) for path, code in files)


def _target(match: Match) -> WrittenTarget:
    if (match,) == EXISTING:
        return WrittenTarget(match.kind)
    return WrittenTarget(match.kind, (*(_place(t) for t in match.places), *(_dotted(n) for n in match.names),
                                      *match.words))


def _place(target: Target) -> str:
    return target.part + ("@any" if target.scope == "any" else "") + ("/" + "/".join(target.sub) if target.sub else "")


def _dotted(name: tuple[str, ...]) -> str:
    return f".{name[1]}" if len(name) == 2 and not name[0] else ".".join(name)
