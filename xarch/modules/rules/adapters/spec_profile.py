"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.kernel.logic.placement import Target
from xarch.modules.rules.domain.values import Fakes, Profile, Scenarios, TestTier
from xarch.modules.spec.contract import Architecture, NoComments, PackageOnly, ScenarioCoverage, Tier


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def architecture(self, location: str) -> Architecture: ...


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
                       fakes=Fakes(architecture.fakes.path[1:], architecture.fakes.stand_in_for)
                       if architecture.fakes is not None else None,
                       each_root=architecture.instance_root(),
                       package_only=tuple(p for g in architecture.guards if isinstance(g, PackageOnly) for p in g.parts),
                       scenarios=next((Scenarios(g.results, g.tier, g.suffix) for g in architecture.guards
                                       if isinstance(g, ScenarioCoverage)), None),
                       no_comments=any(isinstance(g, NoComments) for g in architecture.guards))


def _folders(tree: dict, prefix: tuple[str, ...]) -> list[tuple[str, ...]]:
    found = [prefix]
    for name, sub in tree.items():
        if sub is not None:
            found += _folders(sub, prefix + (name,))
    return found


def _tier(architecture: Architecture, tier: Tier) -> TestTier:
    subject = tuple(Target(s.part, "own" if architecture.parts[s.part].in_instance else "none", s.sub)
                    for s in tier.subject)
    folder = tier.example.path[1:-1] if tier.example is not None else None
    return TestTier(tier.name, subject, folder)
