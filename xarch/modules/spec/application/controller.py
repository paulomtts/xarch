from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.language import LanguageView
from xarch.kernel.logic.placement import Target
from xarch.kernel.logic.testing import ScenarioCoverage, StandIns, TierView
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.explain import (
    cleaned,
    example_of,
    graded,
    held_by,
    key_at,
    nearest,
    overview_keys,
    said,
)
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
    EXAMPLES,
    LOAD,
    AppChosen,
    CheckProfile,
    CheckResult,
    ChooseApp,
    ChooseAppResult,
    DocFile,
    Docs,
    Entry,
    Explain,
    ExplainResult,
    FilesResult,
    FormatExplained,
    GuardsView,
    KeyExplained,
    Migrated,
    MigratedFile,
    MigrateProfile,
    MigrateResult,
    MigrationRefused,
    Need,
    NewProfile,
    NewResult,
    NoProfileChosen,
    OriginResult,
    PartView,
    Problem,
    ProfileChecked,
    ProfileCreated,
    ProfileRefused,
    ProfileSelected,
    ProfileView,
    ProfileViewed,
    ProjectFiles,
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
from xarch.modules.spec.domain.profile_keys import CHOICE_BUNDLED, KEYS, SMALLEST, SYMBOLS, Key
from xarch.modules.spec.domain.values import (
    VERSION,
    Architecture,
    ClosedTree,
    DeadCode,
    Guard,
    Language,
    Layout,
    Loadable,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
    Tier,
    Unloadable,
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
                        entry_point=entry.path[0] if entry is not None else "",
                        package_file=architecture.language.package_file, language=architecture.language.title,
                        reserved=architecture.language.reserved_names, names=architecture.language.names,
                        private=architecture.language.private)

    def profile(self, location: str) -> ProfileView:
        """The profile at a location callers got from select(), a bundled name or a path, as the checks read it;
        raises InvalidArchitecture."""
        return _profile_view(self._architectures.load(location))

    def docs(self, profile: str) -> Docs:
        """The project docs the profile declares, with their text; raises InvalidArchitecture or InvalidTemplate."""
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in self._architectures.docs(profile)))

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult:
        """The files the profile has `init` write beside an app folder called app, with their content; presets off
        leaves out what its folder entries copy. A profile that cannot write them is refused with why."""
        try:
            return ProjectFiles(tuple(self._architectures.files(profile, app, presets)))
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
            return AppChosen(self._selection.app(cmd.start, cmd.given))
        except DomainError as e:
            return ProfileRefused(e.reason)

    def select(self, cmd: SelectProfile) -> SelectResult:
        """No profile asked for or configured comes back with the known ones; an unknown profile, unreadable settings
        or an invalid architecture file is refused with its reason."""
        try:
            name = self._selection.select(cmd.app, cmd.override)
            tests = self._selection.tests(cmd.app, cmd.tests)
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
        files = (MigratedFile(done.profile, None, 0),
                 *(MigratedFile(c.copy.destination, c.copy.source, c.rewritten) for c in done.copies))
        return Migrated(done.folder, done.folder / done.profile, files, done.changes, done.by_hand, cmd.dry_run)

    def explain(self, cmd: Explain) -> ExplainResult:
        """The format of a profile, whole or one key; a key the format does not have comes back with the nearest ones."""
        language = self._architectures.default_language()
        if cmd.key is None:
            shape = tuple(_shown(key, depth, language) for key, depth in overview_keys())
            return FormatExplained(VERSION, shape, tuple(Symbol(said(s, language), said(m, language)) for s, m in SYMBOLS),
                                   SMALLEST)
        key = key_at(cmd.key)
        if key is None:
            return UnknownKey(cleaned(cmd.key), nearest(cleaned(cmd.key)))
        names = self._explanation.choices(key)
        return KeyExplained(plain(key.address), key.where, said(key.meaning, language), said(key.accepts, language),
                            key.required, key.enforced, key.rules, said(example_of(key, names), language), names,
                            tuple(_shown(held, 0, language) for held in held_by(key)),
                            tuple(Need(*graded(fact, language)) for fact in key.needs),
                            language.title if key.needs else "")

    def bundled(self) -> tuple[str, ...]:
        """The names of the bundled profiles: what a key that names one may name."""
        return self._explanation.choices(next(key for key in KEYS if key.choices == CHOICE_BUNDLED))

    def view(self, cmd: ViewProfile) -> ViewResult:
        """The folder tree and import table of a profile; one that cannot be chosen or loaded is refused with why."""
        try:
            loaded = self._review.view(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
        tree, imports = view(loaded.architecture)
        return ProfileViewed(loaded.location, loaded.architecture.name, tree, imports, loaded.bundled)

    def check_profile(self, cmd: CheckProfile) -> CheckResult:
        """Validates a profile: its problems, all at once, with how it differs from the bundled one it is based on; one
        that cannot be chosen is refused with why."""
        try:
            review = self._review.check(cmd.app, cmd.target)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return ProfileRefused(e.reason)
        match review:
            case Unloadable(location, problems):
                return ProfileChecked(location, tuple(Problem(LOAD, text) for text in problems), 0, None)
            case Loadable(location, problems, files, origin):
                return ProfileChecked(location, tuple(Problem(EXAMPLES, text) for text in problems), files, origin)

    def new_profile(self, cmd: NewProfile) -> NewResult:
        """Copies a bundled profile into the project, with its files; a copy that cannot be written is refused with why."""
        try:
            copy = self._creation.create(cmd)
        except DomainError as e:
            return ProfileRefused(e.reason)
        return ProfileCreated(copy.folder, copy.folder / copy.profile, (copy.profile, *copy.pointed), copy.location)


def _entries(tree: Layout) -> tuple[Entry, ...]:
    return tuple(Entry(path, is_dir, leaf) for path, is_dir, leaf in walk(tree))


def _shown(key: Key, depth: int, language: Language) -> Shown:
    return Shown(plain(key.address), depth, said(key.meaning, language), key.required, key.enforced)


def _profile_view(architecture: Architecture) -> ProfileView:
    guards = architecture.guards
    patterns = architecture.patterns()
    parts = tuple(PartView(name, patterns[name], architecture.rules.get(name, ()), part.role, part.litmus,
                           architecture.shown(part), part.untested, architecture.forbidden.get(name, ()),
                           part.must_import, part.holds, part.types_only, part.no_callbacks, part.names, part.built_by,
                           part.shared)
                  for name, part in architecture.parts.items())
    return ProfileView(
        parts=parts, folders=tuple(_folders(architecture.layout, ())),
        tiers=tuple(_tier_view(architecture, tier) for tier in architecture.tiers),
        libraries=None if architecture.libraries is None else dict(architecture.libraries),
        repeats=architecture.repeats, guards=_guards_view(guards),
        fakes=architecture.fakes, framework=architecture.framework, excluded=architecture.excluded,
        hints=dict(architecture.hints),
        language=_language_view(architecture.language),
        reserved=dict(architecture.reserved), approximate=architecture.approximate, checks=dict(architecture.checks))


def _language_view(language: Language) -> LanguageView:
    return LanguageView(language.title, language.extension, language.package_file, language.interface,
                        language.dynamic, language.private, language.special, language.call, language.nothing,
                        language.comment, language.directives, language.shebang, language.encoding,
                        language.branching, language.supplies, language.importing)


def _guards_view(guards: tuple[Guard, ...]) -> GuardsView:
    return GuardsView(
        package_only=tuple(p for g in guards if isinstance(g, PackageOnly) for p in g.parts),
        scenarios=next((g for g in guards if isinstance(g, ScenarioCoverage)), None),
        no_comments=any(isinstance(g, NoComments) for g in guards),
        stand_ins=next((g for g in guards if isinstance(g, StandIns)), None),
        closed_tree=any(isinstance(g, ClosedTree) for g in guards),
        no_duplicates=next((g.min_statements for g in guards if isinstance(g, NoDuplicates)), None),
        no_twins=next((g.min_fields for g in guards if isinstance(g, NoTwins)), None),
        no_twins_renamed=next((g.min_renamed for g in guards if isinstance(g, NoTwins)), None),
        no_twins_subset=next((g.min_subset for g in guards if isinstance(g, NoTwins)), None),
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
