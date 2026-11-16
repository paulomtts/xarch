from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.rules.application.logic import expansion
from xarch.modules.rules.application.logic.expandable import expands
from xarch.modules.rules.application.logic.explained import keyed, uses
from xarch.modules.rules.application.logic.written import written
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.contract import KeyUnset, NoRuleShown, RuleShown
from xarch.modules.rules.domain.rule import Rule
from xarch.profile_values.language import CheckedLanguage


class ExplainingService:
    """The rules a profile's keys expand to, for what `profile explain` shows of the vocabulary: the first rule of the
    profiles given that is written with a word, and the rules a key expands to."""

    def __init__(self, profiles: Profiles):
        self._profiles = profiles

    def example(self, category: str, name: str, locations: tuple[str, ...]) -> tuple[str, Rule] | None:
        """The first rule of the first profile that uses the word, with that profile; a profile that cannot be read
        is passed over."""
        for location in locations:
            for rule in self._rules(location):
                if uses(rule, category, name):
                    return location, rule
        return None

    def language(self, locations: tuple[str, ...]) -> CheckedLanguage:
        """The language of the first of the profiles that can be read; none when none can."""
        for location in locations:
            try:
                return self._profiles.profile(location).language
            except DomainError:
                continue
        return CheckedLanguage()

    def rules_of(self, address: str, location: str) -> list[Rule]:
        """The rules of the profile at location that the key at address expands to; raises DomainError when the
        profile cannot be read."""
        profile = self._profiles.profile(location)
        return keyed([*(rule for rules in expansion.book(profile).values() for rule in rules),
                      *(check.rule for check in profile.checks)], address)

    def rule(self, address: str, location: str) -> RuleShown | KeyUnset | NoRuleShown:
        """The rules the key at address of the profile at location expands to, written as checks; a key the engine
        expands that the profile sets nowhere is unset, and any other key that expands to none says why; raises
        DomainError when the profile cannot be read."""
        rules = self.rules_of(address, location)
        if not rules and expands(address):
            return KeyUnset(address, location)
        if not rules:
            return NoRuleShown(address, location, "it expands to no rule of the engine here: the profile does not set "
                                                  "it, or it is checked by a check of its own")
        return RuleShown(address, location, written(rules, _ids(rules)), len(rules))

    def _rules(self, location: str) -> list[Rule]:
        try:
            profile = self._profiles.profile(location)
        except DomainError:
            return []
        return [rule for rules in expansion.book(profile).values() for rule in rules]


def _ids(rules: list[Rule]) -> list[str]:
    """An id for each rule written as a check: its own, then the part its scope names, then a number when two would
    be the same."""
    ids: list[str] = []
    for rule in rules:
        base = f"{rule.id}-{rule.scope.named_part}" if rule.scope.named_part else rule.id
        name, count = base, 1
        while name in ids:
            count += 1
            name = f"{base}-{count}"
        ids.append(name)
    return ids
