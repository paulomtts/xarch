from __future__ import annotations

from xarch.modules.spec.application.logic.checked_tier import checked_tier
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.layout_walk import docs_name, folders, walk
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import (
    Docs,
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
        language = architecture.language
        repeating = tuple(Repeating(repeat.word, repeat.root, tuple(walk(architecture.instance_tree(repeat))))
                          for repeat in architecture.repeats)
        checked = language.checked
        return Skeleton(top_level=tuple(walk(architecture.top_level_tree())), repeating=repeating,
                        title=checked.title, package_file=checked.package_file, private=checked.private,
                        reserved=language.reserved_names, names=language.names)

    def profile(self, location: str) -> ProfileView:
        architecture = self._architectures.load(location)
        patterns = architecture.patterns()
        parts = tuple(PartView(name, patterns[name], architecture.rules.get(name, ()), part.role, part.litmus,
                               docs_name(architecture, part), part.untested, architecture.forbidden.get(name, ()),
                               part.must_import, part.holds, part.types_only, part.no_callbacks, part.names,
                               part.built_by, part.shared, part.immutable)
                      for name, part in architecture.parts.items())
        return ProfileView(
            parts=parts, folders=folders(architecture.layout),
            tiers=tuple(checked_tier(architecture, tier) for tier in architecture.tiers),
            libraries=None if architecture.libraries is None else dict(architecture.libraries),
            repeats=architecture.repeats, guards=_guards_view(architecture.guards),
            fakes=architecture.fakes, framework=architecture.framework, excluded=architecture.excluded,
            hints=dict(architecture.hints), language=architecture.language.checked,
            reserved=dict(architecture.reserved), approximate=architecture.approximate,
            checks=dict(architecture.checks))

    def docs(self, profile: str) -> Docs:
        """Raises InvalidTemplate too, for a template that cannot be filled."""
        return Docs(root=DOCS_ROOT, files=tuple(self._architectures.docs(profile)))

    def files(self, profile: str, app: str, presets: bool = True) -> ProjectFiles:
        return ProjectFiles(tuple(self._architectures.files(profile, app, presets)))


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
        no_twins_translated=next((g.translated for g in guards if isinstance(g, NoTwins)), ()),
        dead_code=any(isinstance(g, DeadCode) for g in guards),
        untested=any(isinstance(g, DeadCode) and g.untested for g in guards),
        tests_only=any(isinstance(g, DeadCode) and g.tests_only for g in guards),
        pass_through=next((g.parts for g in guards if isinstance(g, PassThrough)), ()),
        private_imports=any(isinstance(g, PrivateImports) for g in guards))
