from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Docs, ProfileRefused, ProfileResult, ProfileSelected, SelectProfile, Skeleton
from xarch.modules.spec.domain.skeleton import DEFAULT_PROFILE


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, service: SkeletonService):
        self._service = service

    def skeleton(self, profile: str = DEFAULT_PROFILE) -> Skeleton:
        """The skeleton of a known profile: callers get the name from select() or profiles()."""
        return self._service.skeleton(profile)

    def docs(self, profile: str = DEFAULT_PROFILE) -> Docs:
        """The project docs and their text; only testing.md's driver row depends on the profile."""
        return self._service.docs(profile)

    def profiles(self) -> tuple[str, ...]:
        return self._service.profiles()

    def select(self, cmd: SelectProfile) -> ProfileResult:
        try:
            name = self._service.select(cmd.app, cmd.override)
        except DomainError as e:                                     # unknown profile, unreadable settings
            return ProfileRefused(e.reason)
        return ProfileSelected(name)
