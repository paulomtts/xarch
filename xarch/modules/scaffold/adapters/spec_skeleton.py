"""Skeleton filled by the spec module: the only file in scaffold that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.scaffold.domain.errors import ProfileUnusable
from xarch.modules.scaffold.domain.values import Language
from xarch.modules.spec.contract import (
    DEFAULT_APP,
    Docs,
    DocsResult,
    Entry,
    FilesResult,
    ProfileRefused,
    ProjectFiles,
    Skeleton,
    SkeletonResult,
)


class _Spec(Protocol):
    """The little scaffold uses of spec's controller."""

    def skeleton(self, profile: str) -> SkeletonResult: ...

    def docs(self, profile: str) -> DocsResult: ...

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult: ...


class SpecSkeleton:
    """Satisfies scaffold's Skeleton port."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return _entries(self._skeleton(profile).top_level)

    def language(self, profile: str) -> Language:
        skeleton = self._skeleton(profile)
        return Language(skeleton.title, skeleton.package_file, skeleton.reserved, skeleton.names, skeleton.private)

    def default_app(self) -> str:
        return DEFAULT_APP

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        return {repeating.word: (repeating.root, _entries(repeating.entries))
                for repeating in self._skeleton(profile).repeating}

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        docs = self._docs(profile)
        return [(docs.root + f.path, f.template) for f in docs.files]

    def files(self, profile: str, app: str) -> list[tuple[tuple[str, ...], str | bytes]]:
        """Raises ProfileUnusable, with spec's reason, when the profile cannot write them."""
        match self._spec.files(profile, app):
            case ProjectFiles(files):
                return [(f.path, f.content) for f in files]
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)

    def _skeleton(self, profile: str) -> Skeleton:
        """Raises ProfileUnusable, with spec's reason, for a profile spec refuses."""
        match self._spec.skeleton(profile):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case Skeleton() as skeleton:
                return skeleton

    def _docs(self, profile: str) -> Docs:
        """Raises ProfileUnusable, with spec's reason, for a profile spec refuses."""
        match self._spec.docs(profile):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case Docs() as docs:
                return docs


def _entries(entries: tuple[Entry, ...]) -> list[tuple[tuple[str, ...], bool]]:
    """What is built: every entry but the optional parts and what lies in them."""
    return [(e.path, e.is_dir) for e in entries if not e.optional and not e.when]
