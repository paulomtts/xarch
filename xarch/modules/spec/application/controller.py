from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.explain import VERSION, cleaned, example_of, held_by, key_at, nearest, overview_keys
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.application.logic.layout_walk import walk
from xarch.modules.spec.application.logic.profile_view import view
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.contract import (
    Architecture,
    CheckProfile,
    CheckResult,
    DocFile,
    Docs,
    Entry,
    Explain,
    ExplainResult,
    FormatExplained,
    KeyExplained,
    Loosened,
    Migrated,
    MigratedFile,
    MigrateProfile,
    MigrateResult,
    MigrationRefused,
    NewProfile,
    NewResult,
    NoProfileChosen,
    Problem,
    ProfileChecked,
    ProfileCreated,
    ProfileOrigin,
    ProfileRefused,
    ProfileSelected,
    ProfileViewed,
    ProjectFile,
    Repeating,
    SelectProfile,
    SelectResult,
    Shown,
    Skeleton,
    Symbol,
    UnknownKey,
    ViewProfile,
    ViewResult,
)
from xarch.modules.spec.domain.errors import NoProfile
from xarch.modules.spec.domain.profile_keys import SMALLEST, SYMBOLS, Key
from xarch.modules.spec.domain.values import Layout, Origin


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, architectures: ArchitectureService, selection: ProfileSelectionService, settings: Settings,
                 review: ProfileReviewService, explanation: ExplainService, migration: MigrationService,
                 creation: ProfileCreationService):
        self._architectures, self._selection, self._settings = architectures, selection, settings
        self._review, self._explanation = review, explanation
        self._migration, self._creation = migration, creation

    def skeleton(self, profile: str) -> Skeleton:
        """The skeleton of a known profile, as callers got its name from select(); raises InvalidArchitecture."""
        architecture = self._architectures.load(profile)
        entry = architecture.entry
        repeating = tuple(Repeating(repeat.word, repeat.root, _entries(architecture.instance_tree(repeat)))
                          for repeat in architecture.repeats)
        return Skeleton(top_level=_entries(architecture.top_level_tree()), repeating=repeating,
                        entry_point=entry.path[0] if entry is not None else "")

    def architecture(self, location: str) -> Architecture:
        """The architecture at a location callers got from select(): a bundled name or a path."""
        return self._architectures.load(location)

    def docs(self, profile: str) -> Docs:
        """The project docs the profile declares, with their text; raises InvalidArchitecture or InvalidTemplate."""
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in self._architectures.docs(profile)))

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]:
        """The files the profile has `init` write beside an app folder called app, with their content; presets off
        leaves out what its folder entries copy. Raises InvalidArchitecture."""
        return tuple(ProjectFile(w.path, w.content, w.pinned, w.preset)
                     for w in self._architectures.files(profile, app, presets))

    def origin(self, location: str) -> ProfileOrigin:
        """Where the profile at a location callers got from select() comes from, and how it is looser than the
        bundled profile it resembles; raises InvalidArchitecture."""
        return _origin(self._architectures.origin(location))

    def configured_app(self, start: Path) -> Path | None:
        """The app folder the project holding the folder start records under [tool.xarch], looked up from start upward,
        or None; raises UnreadableSettings."""
        return self._settings.configured_app(start)

    def select(self, cmd: SelectProfile) -> SelectResult:
        """No profile asked for or configured comes back with the known ones; an unknown profile, unreadable settings
        or an invalid architecture file is refused with its reason."""
        try:
            name, tests = self._selection.select(cmd.app, cmd.override, cmd.tests)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileSelected(name, tests)

    def migrate(self, cmd: MigrateProfile) -> MigrateResult:
        """Converts a profile of format 1 to format 2; a profile it cannot convert, or cannot write, is refused with why."""
        try:
            done = self._migration.migrate(cmd)
        except DomainError as e:
            return MigrationRefused(e.reason)
        return Migrated(done.folder, done.profile, tuple(MigratedFile(*file) for file in done.files), done.changes,
                        done.by_hand, done.dry_run)

    def explain(self, cmd: Explain) -> ExplainResult:
        """The format of a profile, whole or one key; a key the format does not have comes back with the nearest ones."""
        if cmd.key is None:
            shape = tuple(_shown(key, depth) for key, depth in overview_keys())
            return FormatExplained(VERSION, shape, tuple(Symbol(s, m) for s, m in SYMBOLS), SMALLEST)
        key = key_at(cmd.key)
        if key is None:
            return UnknownKey(cleaned(cmd.key), nearest(cleaned(cmd.key)))
        names = self._explanation.choices(key)
        return KeyExplained(plain(key.address), key.where, key.meaning, key.accepts, key.required, key.enforced,
                            key.rules, example_of(key, names), names, tuple(_shown(held, 0) for held in held_by(key)))

    def view(self, cmd: ViewProfile) -> ViewResult:
        """The folder tree and import table of a profile; one that cannot be chosen or loaded is refused with why."""
        try:
            location, architecture, bundled = self._review.view(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
        tree, imports = view(architecture)
        return ProfileViewed(location, architecture.name, tree, imports, bundled)

    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        """Validates a profile: its problems, all at once, with how it differs from the bundled one it is based on; one
        that cannot be chosen is refused with why."""
        try:
            review = self._review.check(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileChecked(review.location, tuple(Problem(check, text) for check, text in review.problems),
                              review.files, _origin(review.origin) if review.origin is not None else None)

    def new_profile(self, cmd: NewProfile) -> NewResult:
        """Copies a bundled profile into the project, with its files; a copy that cannot be written is refused with why."""
        try:
            folder, profile, files, location = self._creation.create(cmd)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileCreated(folder, profile, files, location)


def _entries(tree: Layout) -> tuple[Entry, ...]:
    return tuple(Entry(path, is_dir, leaf) for path, is_dir, leaf in walk(tree))


def _origin(found: Origin) -> ProfileOrigin:
    return ProfileOrigin(found.location, found.bundled, found.closest, found.guards_off, found.baseline_off,
                         tuple(Loosened(item.key, item.part, item.what) for item in found.looser))


def _shown(key: Key, depth: int) -> Shown:
    return Shown(plain(key.address), depth, key.meaning, key.required, key.enforced)
