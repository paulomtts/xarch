from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_in_force import choose
from xarch.modules.spec.application.logic.project_folders import default_app, default_tests
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.folders import Folders
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import AppChosen, KnownProfiles, ProfileSelected


class ProfileSelectionService:
    """Which profile is in force for an app, and which tests root goes with it."""

    def __init__(self, settings: Settings, architectures: ArchitectureService, files: ArchitectureFiles,
                 folders: Folders):
        self._settings, self._architectures, self._files, self._folders = settings, architectures, files, folders

    def app(self, start: Path, given: Path | None) -> AppChosen:
        """The app folder, in full: the one given, read from the folder start when it is relative, else the one the
        project around start records, else the default one in start; raises UnreadableSettings."""
        if given is not None:
            return AppChosen(start / given)
        configured = self._settings.configured_app(start)
        return AppChosen(configured if configured is not None else default_app(start))

    def location(self, app: Path, override: str | None) -> str:
        """The location of the profile in force: the override, else the one configured for the project holding app;
        raises NoProfile, UnknownProfile or UnreadableSettings."""
        configured = None if override is not None else self._settings.configured_profile(app)
        return choose(override, configured, self._files.bundled())

    def select(self, app: Path, override: str | None, tests: Path | None) -> ProfileSelected:
        """The location in force, once its architecture loads, and the tests root that goes with the app; raises
        NoProfile, UnknownProfile, UnreadableSettings or InvalidArchitecture."""
        location = self.location(app, override)
        self._architectures.load(location)
        return ProfileSelected(location, self._tests(app, tests))

    def known(self, app: Path) -> KnownProfiles:
        """The profiles known to the project holding app: the one in force, once its architecture loads, and the
        bundled ones. Raises NoProfile, UnknownProfile, UnreadableSettings or InvalidArchitecture when none is in force
        or it does not load."""
        return KnownProfiles(self.select(app, None, None).name, self._files.bundled())

    def _tests(self, app: Path, given: Path | None) -> Path | None:
        """The tests root that goes with the app, given in full: the one given, else the configured one, else the
        default one when it is a folder, else None; raises UnreadableSettings."""
        if given is not None:
            return given
        configured = self._settings.configured_tests(app)
        if configured is not None:
            return configured
        return next(iter(self._folders.existing([default_tests(app)])), None)
