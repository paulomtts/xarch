from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.language import LanguageView
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

    def language(self, locations: tuple[str, ...]) -> LanguageView:
        """The language of the first of the profiles that can be read; none when none can."""
        for location in locations:
            try:
                return self._profiles.profile(location).language
            except DomainError:
                continue
        return LanguageView()

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
