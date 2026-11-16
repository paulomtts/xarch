"""In-memory implementation of spec's Folders port. Not an adapter: a test double only."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


class FakeFolders:
    """Satisfies spec's Folders: a fixed set of folders (none unless given)."""

    def __init__(self, folders: set[Path] | None = None):
        self._folders = set(folders or ())

    def existing(self, folders: Iterable[Path]) -> tuple[Path, ...]:
        return tuple(folder for folder in folders if folder in self._folders)
