"""Skeleton filled by the spec module: the only file in layout that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.spec.contract import Skeleton


class _Spec(Protocol):                     # the little we use of spec's controller
    def skeleton(self, profile: str) -> Skeleton: ...


class SpecSkeleton:                        # satisfies layout's Skeleton port
    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[str]:
        return [e.path[0] for e in self._spec.skeleton(profile).top_level if len(e.path) == 1]

    def module_parts(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return [(e.path, e.is_dir) for e in self._spec.skeleton(profile).module if e.leaf]
