"""The converted profile written to the disk."""
from __future__ import annotations

from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsProfileOutput:
    """Satisfies spec's ProfileOutput port."""

    def __init__(self, fs: FileSystem):
        self._fs = fs

    def exists(self, path: Path) -> bool:
        return self._fs.exists(path)

    def write(self, path: Path, data: bytes) -> None:
        self._fs.write_bytes(path, data)
