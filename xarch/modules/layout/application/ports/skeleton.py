from __future__ import annotations

from typing import Protocol


class Skeleton(Protocol):
    """What the architecture requires to exist, under a profile."""

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        """Every folder the layout declares outside the repeating folders, at any depth, parents before children."""
        ...

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        """Every file the layout declares outside the repeating folders, at any depth."""
        ...

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        """The folder holding the instances of each repeating folder of the layout, in the order of the profile."""
        ...

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        """(path below an instance, is_dir) for every part that must exist in each instance of the repeating folder
        in root."""
        ...
