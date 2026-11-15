"""In-memory implementation of layout's Skeleton port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.modules.layout.domain.structure import Naming

PYTHON_NAMING = Naming(r"(?!\d)\w+", "_")
"""How Python names a folder, as its data file says."""


class FakeSkeleton:
    """Satisfies layout's Skeleton: the same top-level folders and repeating folders under every profile; repeats
    holds, by the folder of each repeating folder, the parts every instance of it holds; and how the language names
    a folder, Python's unless given."""

    def __init__(self, top_level: list[tuple[str, ...]],
                 repeats: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]] | None = None,
                 top_files: list[tuple[str, ...]] | None = None, naming: Naming = PYTHON_NAMING):
        self._top, self._repeats = list(top_level), dict(repeats or {})
        self._files, self._naming = list(top_files or []), naming

    def naming(self, profile: str) -> Naming:
        return self._naming

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        return list(self._files)

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        return list(self._top)

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        return list(self._repeats)

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        return list(self._repeats[root])
