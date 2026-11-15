"""In-memory implementation of layout's Skeleton port. Not an adapter: a test double only."""
from __future__ import annotations


class FakeSkeleton:
    """Satisfies layout's Skeleton: the same top-level folders, `each` folder and parts under every profile."""

    def __init__(self, top_level: list[str], each_root: tuple[str, ...] | None = None,
                 each_parts: list[tuple[tuple[str, ...], bool]] | None = None, top_files: list[str] | None = None):
        self._top, self._root, self._parts = list(top_level), each_root, list(each_parts or [])
        self._files = list(top_files or [])

    def top_level_files(self, profile: str) -> list[str]:
        return list(self._files)

    def top_level(self, profile: str) -> list[str]:
        return list(self._top)

    def each_root(self, profile: str) -> tuple[str, ...] | None:
        return self._root

    def each_parts(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return list(self._parts)
