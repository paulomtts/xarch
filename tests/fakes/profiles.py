"""In-memory implementation of rules' Profiles port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.modules.rules.domain.errors import ChecksRefused, ProfileUnusable
from xarch.modules.rules.domain.values import InitFile, Profile, Standing


class FakeProfiles:
    """Satisfies rules' Profiles: a fixed Profile per location, with the guards it leaves off and those its baseline
    leaves off too (none unless given), and the init files it writes (none unless given), whatever the app's name; a
    location whose own checks are refused raises ChecksRefused with their problems, and one spec refuses raises
    ProfileUnusable with spec's reason."""

    def __init__(self, profiles: dict[str, Profile], guards: dict[str, Standing] | None = None,
                 files: dict[str, tuple[InitFile, ...]] | None = None, refused: dict[str, tuple[str, ...]] | None = None,
                 unusable: dict[str, str] | None = None):
        self._profiles, self._guards, self._files = profiles, dict(guards or {}), dict(files or {})
        self._refused, self._unusable = dict(refused or {}), dict(unusable or {})

    def profile(self, location: str) -> Profile:
        if location in self._refused:
            raise ChecksRefused(self._refused[location])
        if location in self._unusable:
            raise ProfileUnusable(self._unusable[location])
        return self._profiles[location]

    def standing(self, location: str, app: str) -> Standing:
        guards = self._guards.get(location, Standing((), (), ()))
        return Standing(guards.guards_off, guards.baseline_off, self._files.get(location, ()))
