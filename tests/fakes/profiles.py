"""In-memory implementation of rules' Profiles port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.kernel.logic.origin import Origin
from xarch.modules.rules.domain.values import InitFile, Profile, Standing


class FakeProfiles:
    """Satisfies rules' Profiles: a fixed Profile per location, with its origin (an empty one unless given) and the
    init files it writes (none unless given), whatever the app's name."""

    def __init__(self, profiles: dict[str, Profile], origins: dict[str, Origin] | None = None,
                 files: dict[str, tuple[InitFile, ...]] | None = None):
        self._profiles, self._origins, self._files = profiles, dict(origins or {}), dict(files or {})

    def profile(self, location: str) -> Profile:
        return self._profiles[location]

    def standing(self, location: str, app: str) -> Standing:
        return Standing(self._origins.get(location, Origin()), self._files.get(location, ()))
