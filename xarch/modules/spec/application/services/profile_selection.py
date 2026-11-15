from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_in_force import choose
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService


class ProfileSelectionService:
    """Which profile is in force for an app, and which tests root goes with it."""

    def __init__(self, settings: Settings, architectures: ArchitectureService, files: ArchitectureFiles):
        self._settings, self._architectures, self._files = settings, architectures, files

    def location(self, app: Path, override: str | None) -> str:
        """The location of the profile in force: the override, else the one configured for the project holding app;
        raises NoProfile, UnknownProfile or UnreadableSettings."""
        configured = None if override is not None else self._settings.configured_profile(app)
        return choose(override, configured, self._files.bundled())

    def select(self, app: Path, override: str | None, tests: Path | None = None) -> tuple[str, Path | None]:
        """The location in force, once its architecture loads, and the tests root: the explicit one, else the
        configured one, else None; raises NoProfile, UnknownProfile, UnreadableSettings or InvalidArchitecture."""
        location = self.location(app, override)
        self._architectures.load(location)
        return location, tests if tests is not None else self._settings.configured_tests(app)
