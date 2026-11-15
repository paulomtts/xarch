from __future__ import annotations

from pathlib import Path

from xarch.platform.filesystem import FileSystem


class FsFiles:
    """Satisfies scaffold's Files port."""

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

    def write_bytes(self, path: Path, data: bytes) -> None:
        self._fs.write_bytes(path, data)

    def read_text(self, path: Path) -> str:
        return self._fs.read_text(path)

    def find_upward(self, start: Path, name: str) -> Path | None:
        return self._fs.find_upward(start, name)
