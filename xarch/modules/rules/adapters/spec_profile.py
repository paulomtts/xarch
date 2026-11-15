"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.placement import Target
from xarch.modules.rules.domain.values import (
    Exclusion,
    Fakes,
    Fixture,
    Framework,
    InitFile,
    Loosened,
    Origin,
    PartInfo,
    Profile,
    Scenarios,
    TableForm,
    TestTier,
)
from xarch.modules.rules.domain.values import StandIns as StandInNames
from xarch.modules.spec.contract import (
    Architecture,
    ClosedTree,
    DeadCode,
    NoComments,
    NoDuplicates,
    PackageOnly,
    PassThrough,
    ProfileOrigin,
    ProjectFile,
    ScenarioCoverage,
    StandIns,
    Tier,
)


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def architecture(self, location: str) -> Architecture: ...

    def origin(self, location: str) -> ProfileOrigin: ...

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]: ...


class SpecProfiles:
    """Satisfies rules' Profiles port by translating spec's Architecture."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def profile(self, location: str) -> Profile:
        architecture = self._spec.architecture(location)
        return Profile(parts=architecture.patterns(), rules=dict(architecture.rules),
                       folders=tuple(_folders(architecture.layout, ())),
                       tiers=tuple(_tier(architecture, tier) for tier in architecture.tiers),
                       libraries=None if architecture.libraries is None else dict(architecture.libraries),
                       fakes=Fakes(architecture.fakes.folder, architecture.fakes.stand_in_for,
                                   architecture.fakes.prefix)
                       if architecture.fakes is not None else None,
                       each_root=architecture.instance_root(),
                       package_only=tuple(p for g in architecture.guards if isinstance(g, PackageOnly) for p in g.parts),
                       scenarios=next((Scenarios(g.results, g.tier, g.suffix, g.columns,
                                                 TableForm(g.table.decorator, g.table.row, g.table.id, g.table.keywords),
                                                 g.file)
                                       for g in architecture.guards if isinstance(g, ScenarioCoverage)), None),
                       no_comments=any(isinstance(g, NoComments) for g in architecture.guards),
                       stand_ins=next((StandInNames(g.mocks, g.autospec, g.spec,
                                                    tuple(Fixture(f.name, f.mocks, f.autospec) for f in g.fixtures))
                                       for g in architecture.guards if isinstance(g, StandIns)), None),
                       closed_tree=any(isinstance(g, ClosedTree) for g in architecture.guards),
                       must_import={name: part.must_import for name, part in architecture.parts.items()
                                    if part.must_import},
                       no_duplicates=next((g.min_statements for g in architecture.guards
                                           if isinstance(g, NoDuplicates)), None),
                       dead_code=any(isinstance(g, DeadCode) for g in architecture.guards),
                       pass_through=next((g.parts for g in architecture.guards if isinstance(g, PassThrough)), ()),
                       framework=Framework(architecture.framework.files, architecture.framework.functions,
                                           architecture.framework.skips)
                       if architecture.framework is not None else None,
                       forbidden=dict(architecture.forbidden),
                       info={name: PartInfo(part.role, part.litmus, architecture.shown(part), part.untested)
                             for name, part in architecture.parts.items()},
                       singular=architecture.singular,
                       excluded=tuple(Exclusion(e.path, e.reason) for e in architecture.excluded))


    def origin(self, location: str) -> Origin:
        found = self._spec.origin(location)
        return Origin(found.location, found.bundled, found.closest, found.guards_off, found.baseline_off,
                      tuple(Loosened(item.key, item.part, item.what) for item in found.looser))

    def init_files(self, location: str, app: str) -> tuple[InitFile, ...]:
        """None when the profile cannot write them for this app, which `init` reports when it refuses."""
        try:
            files = self._spec.files(location, app, presets=False)
        except DomainError:
            return ()
        return tuple(InitFile(file.path, _text(file.content), file.pinned) for file in files)


def _text(content: str | bytes) -> str:
    """What `check` compares a pinned file with: a file copied as bytes is compared as the text it holds."""
    return content if isinstance(content, str) else content.decode("utf-8", errors="replace")


def _folders(tree: dict, prefix: tuple[str, ...]) -> list[tuple[str, ...]]:
    found = [prefix]
    for name, sub in tree.items():
        if sub is not None:
            found += _folders(sub, prefix + (name,))
    return found


def _tier(architecture: Architecture, tier: Tier) -> TestTier:
    subject = tuple(Target(s.part, "own" if architecture.parts[s.part].in_instance else "none", s.sub)
                    for s in tier.subject)
    return TestTier(tier.name, subject, tier.folder, tier.types_only, tier.forbidden, tier.proves, tier.may_touch, tier.litmus,
                    tier.one_file_per, tier.may_import)
