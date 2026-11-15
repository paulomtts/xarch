"""Architecture files bundled with xarch as package data (xarch/architectures/<name>.yaml), or anywhere on disk."""
from __future__ import annotations

from collections.abc import Iterator
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureDocument, ArchitectureSource
from xarch.platform.data_files import DataFileError, DataFileReader
from xarch.platform.filesystem import FileSystem

BUNDLED_SUFFIX = ".yaml"
PRESETS = ("presets", "testing")
"""Where the presets of `testing` are, below the bundled folder: one YAML file each, named for the preset."""


def _bundled_folder() -> Traversable:
    return resources.files("xarch").joinpath("architectures")


class FsArchitectureFiles:
    """Satisfies spec's ArchitectureFiles port."""

    def __init__(self, fs: FileSystem, reader: DataFileReader):
        self._fs, self._reader = fs, reader

    def bundled(self) -> tuple[str, ...]:
        return tuple(sorted(f.name.removesuffix(BUNDLED_SUFFIX) for f in _bundled_folder().iterdir()
                            if f.is_file() and f.name.endswith(BUNDLED_SUFFIX)))

    def testing_presets(self) -> dict[str, Any]:
        folder = _bundled_folder().joinpath(*PRESETS)
        found: dict[str, Any] = {}
        for file in sorted(folder.iterdir(), key=lambda f: f.name):
            if file.is_file() and file.name.endswith(BUNDLED_SUFFIX):
                name = file.name.removesuffix(BUNDLED_SUFFIX)
                try:
                    found[name] = self._reader.parse(file.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, DataFileError) as e:
                    raise InvalidArchitecture(f"{'/'.join(PRESETS)}/{file.name}", [f"cannot read the preset: {e}"]) from e
        return found

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        name = _name(source)
        try:
            text = (_bundled_folder().joinpath(name).read_text(encoding="utf-8") if source.bundled
                    else self._fs.read_text(Path(source.location)))
        except (OSError, UnicodeDecodeError) as e:
            raise InvalidArchitecture(name, [f"cannot read the file: {getattr(e, 'strerror', None) or e}"]) from e
        try:
            document = self._reader.parse(text, json_syntax=name.endswith(".json"))
        except DataFileError as e:
            raise InvalidArchitecture(name, e.problems) from e
        return ArchitectureDocument(name, document)

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        if source.bundled:
            return _bundled_folder().joinpath(*Path(relative).parts).is_file()
        return self._fs.is_file(Path(source.location).parent / relative)

    def files_under(self, source: ArchitectureSource, relative: str) -> tuple[str, ...]:
        if source.bundled:
            return tuple(sorted(_below(_bundled_folder().joinpath(*Path(relative).parts))))
        return tuple(self._fs.files_below(Path(source.location).parent / relative))

    def read_bytes(self, source: ArchitectureSource, relative: str) -> bytes:
        try:
            if source.bundled:
                return _bundled_folder().joinpath(*Path(relative).parts).read_bytes()
            return self._fs.read_bytes(Path(source.location).parent / relative)
        except OSError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {e.strerror or e}"]) from e

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        try:
            if source.bundled:
                return _bundled_folder().joinpath(*Path(relative).parts).read_text(encoding="utf-8")
            return self._fs.read_text(Path(source.location).parent / relative)
        except UnicodeDecodeError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': it is not valid UTF-8 text"]) from e
        except OSError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {e.strerror or e}"]) from e


def _below(folder: Traversable, prefix: str = "") -> Iterator[str]:
    if not folder.is_dir():
        return
    for child in folder.iterdir():
        if child.is_dir():
            yield from _below(child, f"{prefix}{child.name}/")
        else:
            yield prefix + child.name


def _name(source: ArchitectureSource) -> str:
    return source.location + BUNDLED_SUFFIX if source.bundled else source.location
