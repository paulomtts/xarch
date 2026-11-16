"""The folders of a project on the disk."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsFolders:
    """Satisfies spec's Folders port."""

    def __init__(self, fs: FileSystem):
        self._fs = fs

    def existing(self, folders: Iterable[Path]) -> tuple[Path, ...]:
        return tuple(folder for folder in folders if self._fs.is_dir(folder))
