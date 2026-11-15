"""In-memory implementation of rules' Profiles port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.modules.rules.domain.values import Profile


class FakeProfiles:
    """Satisfies rules' Profiles: a fixed Profile per location."""

    def __init__(self, profiles: dict[str, Profile]):
        self._profiles = profiles

    def profile(self, location: str) -> Profile:
        return self._profiles[location]
