from __future__ import annotations

from typing import Protocol


class Skeleton(Protocol):
    """What to build: (path, is_dir) for every entry, parents before children."""

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]: ...

    def module(self, profile: str) -> list[tuple[tuple[str, ...], bool]]: ...

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        """(path below the folder holding the app, text) for every project doc."""
        ...
