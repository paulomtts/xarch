from __future__ import annotations

from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsDisk:                              # satisfies layout's Disk port
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def is_dir(self, path: Path) -> bool:
        return self._fs.is_dir(path)

    def is_file(self, path: Path) -> bool:
        return self._fs.is_file(path)

    def subdirectories(self, path: Path) -> list[str]:
        return self._fs.subdirectories(path)
