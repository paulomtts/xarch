"""A new or converted profile written to the disk."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsProfileOutput:
    """Satisfies spec's ProfileOutput port."""

    def __init__(self, fs: FileSystem):
        self._fs = fs

    def taken(self, folder: Path, names: Iterable[str]) -> list[Path]:
        return [folder / name for name in names if self._fs.exists(folder / name)]

    def write(self, folder: Path, outputs: Mapping[str, bytes]) -> None:
        for name, data in outputs.items():
            self._fs.write_bytes(folder / name, data)
