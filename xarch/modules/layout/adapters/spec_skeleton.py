"""Skeleton filled by the spec module: the only file in layout that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.layout.domain.errors import ProfileUnusable
from xarch.modules.layout.domain.structure import Allowed, Beside, Counterpart, Naming, Pattern, Word
from xarch.modules.spec.contract import DEFAULT_TESTS, AcceptedPath, PathPattern, ProfileRefused, Skeleton, SkeletonResult
from xarch.modules.spec.contract import Counterpart as Written


class _Spec(Protocol):
    """The little layout uses of spec's controller."""

    def skeleton(self, profile: str) -> SkeletonResult: ...


class SpecSkeleton:
    """Satisfies layout's Skeleton port."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        return [e.path for e in self._skeleton(profile).top_level if e.is_dir and not e.optional]

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        return [e.path for e in self._skeleton(profile).top_level if not e.is_dir and not e.optional]

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        return [repeating.root for repeating in self._skeleton(profile).repeating]

    def naming(self, profile: str) -> Naming:
        skeleton = self._skeleton(profile)
        return Naming(skeleton.names, skeleton.private)

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        repeating = next(r for r in self._skeleton(profile).repeating if r.root == root)
        return [(e.path, e.is_dir) for e in repeating.entries if e.leaf and not e.optional]

    def when(self, profile: str, root: tuple[str, ...] | None = None) -> dict[tuple[str, ...], tuple[str, ...]]:
        skeleton = self._skeleton(profile)
        entries = (skeleton.top_level if root is None
                   else next(r for r in skeleton.repeating if r.root == root).entries)
        return {e.path: e.when for e in entries if e.when and not e.optional}

    def accepted(self, profile: str) -> list[Allowed]:
        """An entry written tests/<path> is about the folder or file <path> below the tests root."""
        return [Allowed(entry.path[1:], True, "/".join(entry.path), entry.why) if entry.path[0] == DEFAULT_TESTS
                else Allowed(entry.path, False, "/".join(entry.path), entry.why)
                for entry in self._skeleton(profile).accepted]

    def counterparts(self, profile: str) -> list[Counterpart]:
        """A path written tests/<path> is <path> below the tests root."""
        return [Counterpart(item.id, _pattern(item.source), _pattern(item.has),
                            tuple(_pattern(when) for when in item.when),
                            tuple(_allowed(entry, item) for entry in item.accepted), item.message, item.fix)
                for item in self._skeleton(profile).counterparts]

    def words(self, profile: str) -> list[Word]:
        """The names beside the instances are the next step of every folder or file the layout writes below the
        repeating folder's own folder outside it, and of every other repeating folder there."""
        skeleton = self._skeleton(profile)
        paths = [*(entry.path for entry in skeleton.top_level), *(other.root for other in skeleton.repeating)]
        return [Word(each.word, each.root, frozenset(path[len(each.root)] for path in paths
                                                     if len(path) > len(each.root) and path[:len(each.root)] == each.root))
                for each in skeleton.repeating]

    def beside(self, profile: str) -> Beside | None:
        skeleton = self._skeleton(profile)
        return Beside(skeleton.test_files, skeleton.kept) if skeleton.beside else None

    def _skeleton(self, profile: str) -> Skeleton:
        """Raises ProfileUnusable, with spec's reason, for a profile spec refuses."""
        match self._spec.skeleton(profile):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case Skeleton() as skeleton:
                return skeleton


def _pattern(written: PathPattern) -> Pattern:
    tests = written.steps[0] == DEFAULT_TESTS
    return Pattern(written.steps[1:] if tests else written.steps, tests, written.folder)


def _allowed(entry: AcceptedPath, item: Written) -> Allowed:
    """An entry of a counterpart's accepted, a match of its source: a folder when the source is one."""
    tests = entry.path[0] == DEFAULT_TESTS
    written = "/".join(entry.path) + ("/" if item.source.folder else "")
    return Allowed(entry.path[1:] if tests else entry.path, tests, written, entry.why)
