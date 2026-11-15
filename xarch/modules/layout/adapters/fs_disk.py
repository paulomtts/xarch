from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.modules.layout.domain.structure import Requirement
from xarch.platform.filesystem import FileSystem


class FsDisk:
    """Satisfies layout's Disk port."""

    def __init__(self, fs: FileSystem):
        self._fs = fs

    def present(self, root: Path, required: Iterable[Requirement]) -> set[Requirement]:
        found = set()
        for item in required:
            path = root.joinpath(*item.path)
            if self._fs.is_dir(path) if item.is_dir else self._fs.is_file(path):
                found.add(item)
        return found

    def instances(self, root: Path, each: tuple[str, ...]) -> list[str]:
        return self._fs.subdirectories(root.joinpath(*each))

    def below(self, root: Path, each: tuple[str, ...]) -> list[tuple[str, ...]]:
        return self._fs.folders(root.joinpath(*each))

    def working_folder(self) -> Path:
        return Path.cwd()
