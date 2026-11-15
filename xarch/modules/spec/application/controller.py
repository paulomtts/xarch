from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.placement import Target
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.explain import VERSION, cleaned, example_of, held_by, key_at, nearest, overview_keys
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.application.logic.layout_walk import walk
from xarch.modules.spec.application.logic.profile_view import view
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.contract import (
    AppChosen,
    CheckProfile,
    CheckResult,
    ChooseApp,
    ChooseAppResult,
    DocFile,
    Docs,
    Entry,
    ExcludedView,
    Explain,
    ExplainResult,
    FakesView,
    FixtureView,
    FormatExplained,
    FrameworkView,
    GuardsView,
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
    PartView,
    Problem,
    ProfileChecked,
    ProfileCreated,
    ProfileOrigin,
    ProfileRefused,
    ProfileSelected,
    ProfileView,
    ProfileViewed,
    ProjectFile,
    Repeating,
    ScenariosView,
    SelectProfile,
    SelectResult,
    Shown,
    Skeleton,
    StandInsView,
    Symbol,
    TableView,
    TierView,
    UnknownKey,
    ViewProfile,
    ViewResult,
)
from xarch.modules.spec.domain.errors import NoProfile
from xarch.modules.spec.domain.profile_keys import SMALLEST, SYMBOLS, Key
from xarch.modules.spec.domain.values import (
    Architecture,
    ClosedTree,
    DeadCode,
    Guard,
    Layout,
    NoComments,
    NoDuplicates,
    Origin,
    PackageOnly,
    PassThrough,
    PrivateImports,
    ScenarioCoverage,
    StandIns,
    Tier,
)


class SpecController:
    """Publishes the skeleton of a profile, and decides which profile is in force."""

    def __init__(self, architectures: ArchitectureService, selection: ProfileSelectionService,
                 review: ProfileReviewService, explanation: ExplainService, migration: MigrationService,
                 creation: ProfileCreationService):
        self._architectures, self._selection = architectures, selection
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

    def profile(self, location: str) -> ProfileView:
        """The profile at a location callers got from select(), a bundled name or a path, as the checks read it;
        raises InvalidArchitecture."""
        return _profile_view(self._architectures.load(location))

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

    def choose_app(self, cmd: ChooseApp) -> ChooseAppResult:
        """The app folder to work on; settings that cannot be read are refused with why."""
        try:
            return AppChosen(self._selection.app(cmd.start, cmd.given))
        except DomainError as e:
            return ProfileRefused(e.reason)

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
                         tuple(Loosened(item.key, item.part, item.what, item.sentence) for item in found.looser))


def _shown(key: Key, depth: int) -> Shown:
    return Shown(plain(key.address), depth, key.meaning, key.required, key.enforced)


def _profile_view(architecture: Architecture) -> ProfileView:
    guards = architecture.guards
    patterns = architecture.patterns()
    parts = tuple(PartView(name, patterns[name], architecture.rules.get(name, ()), part.role, part.litmus,
                           architecture.shown(part), part.untested, architecture.forbidden.get(name, ()),
                           part.must_import, part.holds, part.types_only, part.no_callbacks, part.names, part.built_by)
                  for name, part in architecture.parts.items())
    return ProfileView(
        parts=parts, folders=tuple(_folders(architecture.layout, ())),
        tiers=tuple(_tier_view(architecture, tier) for tier in architecture.tiers),
        libraries=None if architecture.libraries is None else dict(architecture.libraries),
        repeats=architecture.repeats, guards=_guards_view(guards),
        fakes=FakesView(architecture.fakes.folder, architecture.fakes.stand_in_for, architecture.fakes.prefix)
        if architecture.fakes is not None else None,
        framework=FrameworkView(architecture.framework.files, architecture.framework.functions,
                                architecture.framework.skips) if architecture.framework is not None else None,
        excluded=tuple(ExcludedView(e.path, e.reason) for e in architecture.excluded), hints=dict(architecture.hints))


def _guards_view(guards: tuple[Guard, ...]) -> GuardsView:
    return GuardsView(
        package_only=tuple(p for g in guards if isinstance(g, PackageOnly) for p in g.parts),
        scenarios=next((ScenariosView(g.results, g.tier, g.suffix, g.columns,
                                      TableView(g.table.decorator, g.table.row, g.table.id, g.table.keywords), g.file)
                        for g in guards if isinstance(g, ScenarioCoverage)), None),
        no_comments=any(isinstance(g, NoComments) for g in guards),
        stand_ins=next((StandInsView(g.mocks, g.autospec, g.spec,
                                     tuple(FixtureView(f.name, f.mocks, f.autospec) for f in g.fixtures))
                        for g in guards if isinstance(g, StandIns)), None),
        closed_tree=any(isinstance(g, ClosedTree) for g in guards),
        no_duplicates=next((g.min_statements for g in guards if isinstance(g, NoDuplicates)), None),
        dead_code=any(isinstance(g, DeadCode) for g in guards),
        untested=any(isinstance(g, DeadCode) and g.untested for g in guards),
        pass_through=next((g.parts for g in guards if isinstance(g, PassThrough)), ()),
        private_imports=any(isinstance(g, PrivateImports) for g in guards))


def _tier_view(architecture: Architecture, tier: Tier) -> TierView:
    subject = tuple(Target(s.part, "own" if architecture.parts[s.part].in_instance else "none", s.sub)
                    for s in tier.subject)
    return TierView(tier.name, subject, tier.folder, tier.types_only, tier.forbidden, tier.proves, tier.may_touch,
                    tier.litmus, tier.one_file_per, tier.may_import, tier.must_import)


def _folders(tree: Layout, prefix: tuple[str, ...]) -> list[tuple[str, ...]]:
    found = [prefix]
    for name, sub in tree.items():
        if sub is not None:
            found += _folders(sub, prefix + (name,))
    return found
