"""The data files shipped inside a Python package, below one of its folders, by their path written with `/`. Knows no
module."""
from __future__ import annotations

from collections.abc import Iterator
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path


class PackageData:
    def __init__(self, package: str, folder: str):
        self._package, self._folder = package, folder

    def files_in(self, relative: str = "") -> list[str]:
        """The names of the files directly in the folder at relative, sorted; [] if it is no folder."""
        folder = self._at(relative)
        return sorted(child.name for child in folder.iterdir() if child.is_file()) if folder.is_dir() else []

    def files_below(self, relative: str) -> list[str]:
        """Every file below the folder at relative, at any depth, as its path in it written with `/`, sorted; [] if it
        is no folder."""
        return sorted(_below(self._at(relative)))

    def is_file(self, relative: str) -> bool:
        return self._at(relative).is_file()

    def read_text(self, relative: str) -> str:
        """The text of the file, as UTF-8; raises OSError or UnicodeDecodeError."""
        return self._at(relative).read_text(encoding="utf-8")

    def read_bytes(self, relative: str) -> bytes:
        """The bytes of the file; raises OSError."""
        return self._at(relative).read_bytes()

    def _at(self, relative: str) -> Traversable:
        return resources.files(self._package).joinpath(self._folder, *Path(relative).parts)


def _below(folder: Traversable, prefix: str = "") -> Iterator[str]:
    if not folder.is_dir():
        return
    for child in folder.iterdir():
        if child.is_dir():
            yield from _below(child, f"{prefix}{child.name}/")
        else:
            yield prefix + child.name
