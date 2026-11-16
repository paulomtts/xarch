"""Skeleton filled by the spec module: the only file in layout that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.layout.domain.errors import ProfileUnusable
from xarch.modules.layout.domain.structure import Naming
from xarch.modules.spec.contract import ProfileRefused, Skeleton, SkeletonResult


class _Spec(Protocol):
    """The little layout uses of spec's controller."""

    def skeleton(self, profile: str) -> SkeletonResult: ...


class SpecSkeleton:
    """Satisfies layout's Skeleton port."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        return [e.path for e in self._skeleton(profile).top_level if e.is_dir]

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        return [e.path for e in self._skeleton(profile).top_level if not e.is_dir]

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        return [repeating.root for repeating in self._skeleton(profile).repeating]

    def naming(self, profile: str) -> Naming:
        skeleton = self._skeleton(profile)
        return Naming(skeleton.names, skeleton.language.private)

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        repeating = next(r for r in self._skeleton(profile).repeating if r.root == root)
        return [(e.path, e.is_dir) for e in repeating.entries if e.leaf]

    def _skeleton(self, profile: str) -> Skeleton:
        """Raises ProfileUnusable, with spec's reason, for a profile spec refuses."""
        match self._spec.skeleton(profile):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case Skeleton() as skeleton:
                return skeleton
