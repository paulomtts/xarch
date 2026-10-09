from __future__ import annotations

from typing import Protocol


class Skeleton(Protocol):
    """What the architecture requires to exist, under a profile."""

    def top_level(self, profile: str) -> list[str]: ...

    def module_parts(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        """(path below the module, is_dir) for every part that must exist in each module."""
        ...
