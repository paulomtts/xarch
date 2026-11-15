from __future__ import annotations

from typing import Protocol


class Skeleton(Protocol):
    """What the architecture requires to exist, under a profile."""

    def top_level(self, profile: str) -> list[str]: ...

    def top_level_files(self, profile: str) -> list[str]:
        """The files the layout declares directly below the app root."""
        ...

    def each_root(self, profile: str) -> tuple[str, ...] | None:
        """The folder holding the instances of the layout's `each` folder, or None if it has none."""
        ...

    def each_parts(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        """(path below an instance, is_dir) for every part that must exist in each instance."""
        ...
