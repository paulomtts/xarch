from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.application.services.publishing import PublishingService
from xarch.modules.spec.contract import (
    CheckProfile,
    CheckResult,
    ChooseApp,
    ChooseAppResult,
    DocsResult,
    Explain,
    ExplainResult,
    FilesResult,
    FilesTaken,
    MigrateProfile,
    MigrateResult,
    MigrationRefused,
    NewProfile,
    NewResult,
    NoProfileChosen,
    OriginResult,
    ProfileRefused,
    ProfileResult,
    SelectProfile,
    SelectResult,
    SkeletonResult,
    ViewProfile,
    ViewResult,
)
from xarch.modules.spec.domain.errors import NoProfile, WouldOverwrite
from xarch.modules.spec.domain.profile_keys import CHOICE_BUNDLED, KEYS


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, architectures: ArchitectureService, selection: ProfileSelectionService,
                 review: ProfileReviewService, explanation: ExplainService, migration: MigrationService,
                 creation: ProfileCreationService, publishing: PublishingService):
        self._architectures, self._selection = architectures, selection
        self._review, self._explanation = review, explanation
        self._migration, self._creation, self._publishing = migration, creation, publishing

    def skeleton(self, profile: str) -> SkeletonResult:
        """The skeleton of a profile, as callers got its name from select(); one that does not load is refused with
        why."""
        try:
            return self._publishing.skeleton(profile)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def profile(self, location: str) -> ProfileResult:
        """The profile at a location callers got from select(), a bundled name or a path, as the checks read it; one
        that does not load is refused with why."""
        try:
            return self._publishing.profile(location)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def docs(self, profile: str) -> DocsResult:
        """The project docs the profile declares, with their text; a profile that does not load, or a template that
        cannot be filled, is refused with why."""
        try:
            return self._publishing.docs(profile)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult:
        """The files the profile has `init` write beside an app folder called app, with their content; presets off
        leaves out what its folder entries copy. A profile that cannot write them is refused with why."""
        try:
            return self._publishing.files(profile, app, presets)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def origin(self, location: str) -> OriginResult:
        """Where the profile at a location callers got from select() comes from, and how it is looser than the
        bundled profile it resembles; a profile that cannot be loaded is refused with why."""
        try:
            return self._architectures.origin(location)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def choose_app(self, cmd: ChooseApp) -> ChooseAppResult:
        """The app folder to work on; settings that cannot be read are refused with why."""
        try:
            return self._selection.app(cmd.start, cmd.given)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def select(self, cmd: SelectProfile) -> SelectResult:
        """No profile asked for or configured comes back with the known ones; an unknown profile, unreadable settings
        or an invalid architecture file is refused with its reason."""
        try:
            return self._selection.select(cmd.app, cmd.override, cmd.tests)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def migrate(self, cmd: MigrateProfile) -> MigrateResult:
        """Converts a profile of format 1 to format 2; one that would be written over files is refused naming them, and
        one it cannot convert, or cannot write, with why."""
        try:
            return self._migration.migrate(cmd)
        except WouldOverwrite as e:
            return FilesTaken(e.taken)
        except DomainError as e:
            return MigrationRefused(e.reason)

    def explain(self, cmd: Explain) -> ExplainResult:
        """The format of a profile, whole or one key; a key the format does not have comes back with the nearest ones,
        and the data file of a language that does not load is refused with why."""
        try:
            return self._explanation.explain(cmd.key)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def bundled(self) -> tuple[str, ...]:
        """The names of the bundled profiles: what a key that names one may name."""
        return self._explanation.choices(next(key for key in KEYS if key.choices == CHOICE_BUNDLED))

    def view(self, cmd: ViewProfile) -> ViewResult:
        """The folder tree and import table of a profile; one that cannot be chosen or loaded is refused with why."""
        try:
            return self._review.view(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        """Validates a profile: its problems, all at once, with how it differs from the bundled one it is based on; one
        that cannot be chosen is refused with why."""
        try:
            return self._review.check(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)

    def new_profile(self, cmd: NewProfile) -> NewResult:
        """Copies a bundled profile into the project, with its files; a copy that would be written over files is refused
        naming them, and one that cannot be written with why."""
        try:
            return self._creation.create(cmd)
        except WouldOverwrite as e:
            return FilesTaken(e.taken)
        except DomainError as e:
            return ProfileRefused(e.reason)

