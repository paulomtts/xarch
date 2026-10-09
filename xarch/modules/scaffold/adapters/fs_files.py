from __future__ import annotations

from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsFiles:                             # satisfies scaffold's Files port
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def exists(self, path: Path) -> bool:
        return self._fs.exists(path)

    def is_dir(self, path: Path) -> bool:
        return self._fs.is_dir(path)

    def create_empty(self, path: Path) -> None:
        self._fs.create_empty(path)

    def write_text(self, path: Path, text: str) -> None:
        self._fs.write_text(path, text)
