"""A rule as the profile would write it as a check of its own (see profile_values' checks): what `xarch profile explain
<key> --rule` shows of a key's rules, so that a check xarch has reads as a check a profile could write. A rule written
so and read back is the same rule, its id and key aside: a check of one's own takes an id of its own, and its key is
`checks.<id>`. The text of it is the check format's.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from xarch.kernel.logic.names import outside_text
from xarch.kernel.logic.targets import written_target
from xarch.modules.rules.domain.rule import MUST_BE_REACHED, Match, OwnCheck, Rule
from xarch.modules.rules.domain.vocabulary import TARGETS
from xarch.profile_values.checks import Quantified, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage

_IMPORT = re.compile(r"%import (?P<dotted>[^ %]+) (?P<name>[^ %]+)%")
"""The token of a line that imports a name from a file of the app, in the code of a check written for the
explanation."""
_WORKED = {"subclass": ("name", "base")}
"""The tokens of the code of a check written for the explanation that the language's `worked` templates fill in, each
`%<template> <value> ...%`, with the placeholders its values stand for, in order."""
_VALUED = frozenset(kind.name for kind in TARGETS if kind.values)
"""The kinds of target that take values: a check writes one with its values, even none, and any other alone."""


def written(rules: Iterable[Rule], member: str, *, words: Mapping[str, str]) -> dict[str, WrittenCheck]:
    """The rules as checks of a profile, each under an id of its own (see _ids), an outside name joined with the
    language's member, a place written as a reference with words, the word of the repeating folder each part of the
    profile lies in."""
    rules = list(rules)
    return {name: check_of(rule, member, words=words) for rule, name in zip(rules, _ids(rules))}


def written_own(checks: Iterable[OwnCheck], language: CheckedLanguage) -> dict[str, WrittenCheck]:
    """Checks of a profile's own as its `checks` are written, each under its id with its examples, the tokens of the
    language (see _tokens_filled) in their paths and code filled in; checks written for the explanation, which name no
    place, so no word is needed."""
    return {own.rule.id: check_of(own.rule, language.member, _filled(own.flagged, language), _filled(own.clean, language),
                                  words={})
            for own in checks}


def _ids(rules: list[Rule]) -> list[str]:
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


def check_of(rule: Rule, member: str, flagged: tuple[tuple[str, str], ...] = (),
             clean: tuple[tuple[str, str], ...] = (), *, words: Mapping[str, str]) -> WrittenCheck:
    """The rule as the check a profile would write, with the examples given, an outside name joined with member, a place
    written as a reference with words (see written_target); raises ValueError for a place in the own instance of a part
    words gives no word."""
    targets = () if rule.quantifier == MUST_BE_REACHED else tuple(_target(match, member, words) for match in rule.targets)
    quantified = Quantified(rule.quantifier, targets, rule.links, rule.via, rule.roots, rule.spread, rule.elsewhere)
    return WrittenCheck(rule.facts, rule.scope, quantified, rule.sayings, rule.keep, rule.exempt, rule.mode, flagged,
                        clean)


def _tokens_filled(text: str, language: CheckedLanguage) -> str:
    """The text with the tokens of the language filled in: `%extension%`, `%comment%`, `%import <dotted> <name>%`, a
    line that imports name from the file of the app that dotted names, as the language's importing says, and each
    token of _WORKED, as the language's worked template of that name writes it (each left as written when the language
    does not say)."""
    text = text.replace("%extension%", language.extension).replace("%comment%", language.comment)
    for template, placeholders in _WORKED.items():
        form = getattr(language.worked, template)
        if form:
            token = re.compile(rf"%{template}{' ([^ %]+)' * len(placeholders)}%")
            text = token.sub(lambda found, form=form, held=placeholders: _fill(form, dict(zip(held, found.groups()))),
                             text)
    if not language.importing:
        return text
    return _IMPORT.sub(lambda found: language.importing.format(dotted=found["dotted"], name=found["name"]), text)


def _fill(template: str, values: Mapping[str, str]) -> str:
    """The template with each `{<name>}` of the values replaced in one pass, any other text kept as it is."""
    return re.sub("{(" + "|".join(values) + ")}", lambda found: values[found.group(1)], template)


def _filled(files: tuple[tuple[str, str], ...], language: CheckedLanguage) -> tuple[tuple[str, str], ...]:
    return tuple((_tokens_filled(path, language), _tokens_filled(code, language)) for path, code in files)


def _target(match: Match, member: str, words: Mapping[str, str]) -> WrittenTarget:
    if match.kind not in _VALUED:
        return WrittenTarget(match.kind)
    return WrittenTarget(match.kind, (*(written_target(place, words) for place in match.places),
                                      *(outside_text(n, member) for n in match.names), *match.words))
