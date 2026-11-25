"""In-memory implementation of rules' Profiles port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.modules.rules.domain.errors import ChecksRefused, ProfileUnusable
from xarch.modules.rules.domain.outcomes import InitFile, Known, Standing
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import KeyFacts, Reviewed


class FakeProfiles:
    """Satisfies rules' Profiles: a fixed Profile per location, with the guards it leaves off, those its baseline
    leaves off too and the parts it redefines without their litmus (none unless given), and the init files it writes
    (none unless given), whatever the app's name; the profiles a project knows (none in force and those given as the
    bundled ones, unless known says; a DomainError there is raised), what the format says of a key (nothing unless
    given; a DomainError there is raised); a location whose own checks are refused raises ChecksRefused with
    their problems, and one spec refuses raises ProfileUnusable with spec's reason. Every against reviewed is asked
    with is kept in against, in order."""

    def __init__(self, profiles: dict[str, Profile], guards: dict[str, Standing] | None = None,
                 files: dict[str, tuple[InitFile, ...]] | None = None, refused: dict[str, tuple[str, ...]] | None = None,
                 unusable: dict[str, str] | None = None, known: Known | DomainError | None = None,
                 keys: dict[str, KeyFacts | DomainError] | None = None,
                 reviewed: dict[str | None, Reviewed | DomainError] | None = None):
        self._profiles, self._guards, self._files = profiles, dict(guards or {}), dict(files or {})
        self._known = Known(None, tuple(profiles)) if known is None else known
        self._keys, self._reviewed = dict(keys or {}), dict(reviewed or {})
        self._refused, self._unusable = dict(refused or {}), dict(unusable or {})
        self.against: list[str | None] = []

    def profile(self, location: str) -> Profile:
        if location in self._refused:
            raise ChecksRefused(self._refused[location])
        if location in self._unusable:
            raise ProfileUnusable(self._unusable[location])
        return self._profiles[location]

    def known(self, app: Path) -> Known:
        if isinstance(self._known, DomainError):
            raise self._known
        return self._known

    def key(self, address: str) -> KeyFacts:
        found = self._keys.get(address, KeyFacts())
        if isinstance(found, DomainError):
            raise found
        return found

    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        self.against.append(against)
        found = self._reviewed[target]
        if isinstance(found, DomainError):
            raise found
        return found

    def standing(self, location: str, app: str) -> Standing:
        guards = self._guards.get(location, Standing((), (), ()))
        return Standing(guards.guards_off, guards.baseline_off, self._files.get(location, ()), guards.looser)
