from __future__ import annotations

from pathlib import Path

from xarch.modules.scaffold.domain.values import FILE, FOLDER, PYPROJECT
from xarch.platform.filesystem import FileSystem


class FsFiles:
    """Satisfies scaffold's Files port."""

    def __init__(self, fs: FileSystem):
        self._fs = fs

    def kind(self, path: Path) -> str | None:
        if self._fs.is_dir(path):
            return FOLDER
        return FILE if self._fs.exists(path) else None

    def lay_down(self, path: Path, content: str | bytes) -> None:
        if isinstance(content, bytes):
            self._fs.write_bytes(path, content)
        elif content:
            self._fs.write_text(path, content)
        else:
            self._fs.create_empty(path)

    def pyproject(self, start: Path) -> tuple[Path, str] | None:
        found = self._fs.find_upward(start, PYPROJECT)
        return None if found is None else (found, self._fs.read_text(found))

    def resolved(self, folder: Path, path: Path) -> Path:
        return self._fs.real(folder / path)
