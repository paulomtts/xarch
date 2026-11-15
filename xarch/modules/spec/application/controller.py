from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreation
from xarch.modules.spec.application.services.profile_review import ProfileReview
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import (
    Architecture,
    CheckProfile,
    CheckResult,
    Docs,
    Explain,
    ExplainResult,
    MigrateProfile,
    MigrateResult,
    MigrationRefused,
    NewProfile,
    NewResult,
    ProfileOrigin,
    ProfileRefused,
    ProfileResult,
    ProfileSelected,
    ProjectFile,
    SelectProfile,
    Skeleton,
    ViewProfile,
    ViewResult,
)


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, service: SkeletonService, architectures: ArchitectureService,
                 settings: Settings, files: ArchitectureFiles, migration: MigrationService | None = None, *,
                 creation: ProfileCreation | None = None):
        self._service, self._architectures, self._settings, self._files = service, architectures, settings, files
        self._migration, self._creation = migration, creation
        self._explanation, self._review = ExplainService(files), ProfileReview(settings, architectures, files)

    def skeleton(self, profile: str) -> Skeleton:
        """The skeleton of a known profile: callers get the name from select() or profiles()."""
        return self._service.skeleton(profile)

    def architecture(self, location: str) -> Architecture:
        """The architecture at a location callers got from select(): a bundled name or a path."""
        return self._architectures.load(location)

    def docs(self, profile: str) -> Docs:
        """The project docs the profile declares, with their text."""
        return self._architectures.docs(profile)

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]:
        """The files the profile has `init` write beside an app folder called app, with their content; presets off
        leaves out what its folder entries copy."""
        return self._architectures.files(profile, app, presets)

    def origin(self, location: str) -> ProfileOrigin:
        """Where the profile at a location callers got from select() comes from, and how it is looser than the
        bundled profile it resembles."""
        return self._architectures.origin(location)

    def configured_app(self, start: Path) -> Path | None:
        """The app folder the project holding the folder start records under [tool.xarch], looked up from start upward,
        or None; raises UnreadableSettings."""
        return self._settings.configured_app(start)

    def profiles(self) -> tuple[str, ...]:
        return self._files.bundled()

    def select(self, cmd: SelectProfile) -> ProfileResult:
        """An unknown profile, unreadable settings or an invalid architecture file is refused with its reason."""
        try:
            name, tests = self._service.select(cmd.app, cmd.override, cmd.tests)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileSelected(name, tests)

    def migrate(self, cmd: MigrateProfile) -> MigrateResult:
        """Converts a profile of format 1 to format 2; a profile it cannot convert, or cannot write, is refused with why."""
        if self._migration is None:
            return MigrationRefused("migration is not available")
        try:
            return self._migration.migrate(cmd)
        except DomainError as e:
            return MigrationRefused(e.reason)

    def explain(self, cmd: Explain) -> ExplainResult:
        """The format of a profile, whole or one key; a key the format does not have comes back with the nearest ones."""
        return self._explanation.explain(cmd)

    def view(self, cmd: ViewProfile) -> ViewResult:
        """The folder tree and import table of a profile; one that cannot be chosen or loaded is refused with why."""
        try:
            return self._review.view(cmd)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        """Validates a profile: its problems, all at once, with how it differs from the bundled one it is based on; one
        that cannot be chosen is refused with why."""
        try:
            return self._review.check(cmd)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def new_profile(self, cmd: NewProfile) -> NewResult:
        """Copies a bundled profile into the project, with its files; a copy that cannot be written is refused with why."""
        if self._creation is None:
            return ProfileRefused("creating a profile is not available")
        try:
            return self._creation.create(cmd)
        except DomainError as e:
            return ProfileRefused(e.reason)
