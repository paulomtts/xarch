"""Skeleton filled by the spec module: the only file in scaffold that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.spec.contract import Docs, Entry, Skeleton


class _Spec(Protocol):
    """The little scaffold uses of spec's controller."""

    def skeleton(self, profile: str) -> Skeleton: ...

    def docs(self, profile: str) -> Docs: ...


class SpecSkeleton:
    """Satisfies scaffold's Skeleton port."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return _entries(self._spec.skeleton(profile).top_level)

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        skeleton = self._spec.skeleton(profile)
        if skeleton.each_root is None:
            return {}
        return {"/".join(skeleton.each_root): (skeleton.each_root, _entries(skeleton.each))}

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        docs = self._spec.docs(profile)
        return [(docs.root + f.path, f.template) for f in docs.files]


def _entries(entries: tuple[Entry, ...]) -> list[tuple[tuple[str, ...], bool]]:
    return [(e.path, e.is_dir) for e in entries]
