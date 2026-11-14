"""Architecture files bundled with xarch as package data (xarch/architectures/<name>.yaml), or anywhere on disk."""
from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureDocument, ArchitectureSource
from xarch.platform.data_files import DataFileError, DataFileReader
from xarch.platform.filesystem import FileSystem

BUNDLED_SUFFIX = ".yaml"


def _bundled_folder() -> Traversable:
    return resources.files("xarch").joinpath("architectures")


class FsArchitectureFiles:                 # satisfies spec's ArchitectureFiles port
    def __init__(self, fs: FileSystem, reader: DataFileReader):
        self._fs, self._reader = fs, reader

    def bundled(self) -> tuple[str, ...]:
        return tuple(sorted(f.name.removesuffix(BUNDLED_SUFFIX) for f in _bundled_folder().iterdir()
                            if f.is_file() and f.name.endswith(BUNDLED_SUFFIX)))

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

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        try:
            if source.bundled:
                return _bundled_folder().joinpath(*Path(relative).parts).read_text(encoding="utf-8")
            return self._fs.read_text(Path(source.location).parent / relative)
        except (OSError, UnicodeDecodeError) as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {getattr(e, 'strerror', None) or e}"]) from e


def _name(source: ArchitectureSource) -> str:
    return source.location + BUNDLED_SUFFIX if source.bundled else source.location
