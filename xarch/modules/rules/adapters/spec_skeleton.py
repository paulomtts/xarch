"""Skeleton filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.rules.domain.values import Parts
from xarch.modules.spec.contract import Skeleton


class _Spec(Protocol):                     # the little we use of spec's controller
    def skeleton(self, profile: str) -> Skeleton: ...


class SpecSkeleton:                        # satisfies rules' Skeleton port
    def __init__(self, spec: _Spec):
        self._spec = spec

    def parts(self, profile: str) -> Parts:
        skeleton = self._spec.skeleton(profile)
        top = {e.path[0] for e in skeleton.top_level if len(e.path) == 1}
        module = {e.path[0] for e in skeleton.module if len(e.path) == 1}
        application = {e.path[1].removesuffix(".py") for e in skeleton.module
                       if len(e.path) == 2 and e.path[0] == "application"}
        return Parts(frozenset(top - {"modules", skeleton.entry_point}), frozenset(module - {"application"}),
                     frozenset(application), skeleton.entry_point)
