from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import (Architecture, Docs, ProfileRefused, ProfileResult, ProfileSelected,
                                         SelectProfile, Skeleton)


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, service: SkeletonService, architectures: ArchitectureService):
        self._service, self._architectures = service, architectures

    def skeleton(self, profile: str) -> Skeleton:
        """The skeleton of a known profile: callers get the name from select() or profiles()."""
        return self._service.skeleton(profile)

    def architecture(self, location: str) -> Architecture:
        """The architecture at a location callers got from select(): a bundled name or a path."""
        return self._architectures.load(location)

    def docs(self, profile: str) -> Docs:
        """The project docs the profile declares, with their text."""
        return self._architectures.docs(profile)

    def profiles(self) -> tuple[str, ...]:
        return self._service.profiles()

    def select(self, cmd: SelectProfile) -> ProfileResult:
        """An unknown profile, unreadable settings or an invalid architecture file is refused with its reason."""
        try:
            name, tests = self._service.select(cmd.app, cmd.override, cmd.tests)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileSelected(name, tests)
