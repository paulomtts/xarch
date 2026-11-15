"""Skeleton filled by the spec module: the only file in scaffold that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.spec.contract import Docs, Entry, ProjectFile, Skeleton


class _Spec(Protocol):
    """The little scaffold uses of spec's controller."""

    def skeleton(self, profile: str) -> Skeleton: ...

    def docs(self, profile: str) -> Docs: ...

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]: ...


class SpecSkeleton:
    """Satisfies scaffold's Skeleton port."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return _entries(self._spec.skeleton(profile).top_level)

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        return {repeating.word: (repeating.root, _entries(repeating.entries))
                for repeating in self._spec.skeleton(profile).repeating}

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        docs = self._spec.docs(profile)
        return [(docs.root + f.path, f.template) for f in docs.files]

    def files(self, profile: str, app: str) -> list[tuple[tuple[str, ...], str | bytes]]:
        return [(f.path, f.content) for f in self._spec.files(profile, app)]


def _entries(entries: tuple[Entry, ...]) -> list[tuple[tuple[str, ...], bool]]:
    return [(e.path, e.is_dir) for e in entries]
