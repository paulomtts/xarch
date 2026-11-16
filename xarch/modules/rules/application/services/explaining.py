from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.rules.application.logic import expansion
from xarch.modules.rules.application.logic.explained import keyed, uses
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.domain.rule import Rule


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

    def first_of(self, address: str, locations: tuple[str, ...]) -> tuple[str, Rule] | None:
        """The first rule a key expands to in the first of the profiles that sets it, with that profile."""
        for location in locations:
            found = keyed(self._rules(location), address)
            if found:
                return location, found[0]
        return None

    def rules_of(self, address: str, location: str) -> list[Rule]:
        """The rules of the profile at location that the key at address expands to; raises DomainError when the
        profile cannot be read."""
        profile = self._profiles.profile(location)
        return keyed([*(rule for rules in expansion.book(profile).values() for rule in rules),
                      *(check.rule for check in profile.checks)], address)

    def _rules(self, location: str) -> list[Rule]:
        try:
            profile = self._profiles.profile(location)
        except DomainError:
            return []
        return [rule for rules in expansion.book(profile).values() for rule in rules]
