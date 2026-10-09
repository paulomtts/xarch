"""Skeleton filled by the spec module: the only file in scaffold that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.spec.contract import Docs, Entry, Skeleton


class _Spec(Protocol):                     # the little we use of spec's controller
    def skeleton(self, profile: str) -> Skeleton: ...

    def docs(self) -> Docs: ...


class SpecSkeleton:                        # satisfies scaffold's Skeleton port
    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return _entries(self._spec.skeleton(profile).top_level)

    def module(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return _entries(self._spec.skeleton(profile).module)

    def docs(self) -> list[tuple[tuple[str, ...], str]]:
        docs = self._spec.docs()
        return [(docs.root + f.path, f.template) for f in docs.files]


def _entries(entries: tuple[Entry, ...]) -> list[tuple[tuple[str, ...], bool]]:
    return [(e.path, e.is_dir) for e in entries]
