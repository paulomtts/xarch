from __future__ import annotations

from xarch.modules.spec.application.logic.checked_tier import checked_tier
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.layout_walk import docs_name, walk
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import (
    DocFile,
    Docs,
    Entry,
    GuardsView,
    PartView,
    ProfileView,
    ProjectFiles,
    Repeating,
    Skeleton,
)
from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    Guard,
    Layout,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
)
from xarch.profile_values.testing import ScenarioCoverage, StandIns


class PublishingService:
    """Assembles what spec hands out of a profile: its skeleton, the profile as the checks read it, its project docs
    and the files `init` writes. Each raises InvalidArchitecture for a profile that does not load."""

    def __init__(self, architectures: ArchitectureService):
        self._architectures = architectures

    def skeleton(self, profile: str) -> Skeleton:
        architecture = self._architectures.load(profile)
        entry = architecture.entry
        language = architecture.language
        repeating = tuple(Repeating(repeat.word, repeat.root, _entries(architecture.instance_tree(repeat)))
                          for repeat in architecture.repeats)
        return Skeleton(top_level=_entries(architecture.top_level_tree()), repeating=repeating,
                        entry_point=entry.path[0] if entry is not None else "",
                        package_file=language.checked.package_file, language=language.checked.title,
                        reserved=language.reserved_names, names=language.names, private=language.checked.private)

    def profile(self, location: str) -> ProfileView:
        architecture = self._architectures.load(location)
        patterns = architecture.patterns()
        parts = tuple(PartView(name, patterns[name], architecture.rules.get(name, ()), part.role, part.litmus,
                               docs_name(architecture, part), part.untested, architecture.forbidden.get(name, ()),
                               part.must_import, part.holds, part.types_only, part.no_callbacks, part.names,
                               part.built_by, part.shared)
                      for name, part in architecture.parts.items())
        return ProfileView(
            parts=parts, folders=((), *(path for path, is_dir, _ in walk(architecture.layout) if is_dir)),
            tiers=tuple(checked_tier(architecture, tier) for tier in architecture.tiers),
            libraries=None if architecture.libraries is None else dict(architecture.libraries),
            repeats=architecture.repeats, guards=_guards_view(architecture.guards),
            fakes=architecture.fakes, framework=architecture.framework, excluded=architecture.excluded,
            hints=dict(architecture.hints), language=architecture.language.checked,
            reserved=dict(architecture.reserved), approximate=architecture.approximate,
            checks=dict(architecture.checks))

    def docs(self, profile: str) -> Docs:
        """Raises InvalidTemplate too, for a template that cannot be filled."""
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in self._architectures.docs(profile)))

    def files(self, profile: str, app: str, presets: bool = True) -> ProjectFiles:
        return ProjectFiles(tuple(self._architectures.files(profile, app, presets)))


def _entries(tree: Layout) -> tuple[Entry, ...]:
    return tuple(Entry(path, is_dir, leaf) for path, is_dir, leaf in walk(tree))


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
