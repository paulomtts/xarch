"""Architecture files bundled with xarch as package data (xarch/architectures/<name>.yaml), or anywhere on disk."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import PROFILE_SUFFIX, ArchitectureDocument, ArchitectureSource
from xarch.platform.data_files import DataFileError, DataFileReader
from xarch.platform.filesystem import FileSystem
from xarch.platform.package_data import PackageData

PRESETS = "presets/testing"
"""Where the presets of `testing` are, below the bundled folder: one YAML file each, named for the preset."""
LANGUAGES = "presets/language"
"""Where the data files of the languages are, below the bundled folder: one YAML file each, named for the language."""


class FsArchitectureFiles:
    """Satisfies spec's ArchitectureFiles port: a bundled architecture from the package data, any other on disk."""

    def __init__(self, fs: FileSystem, reader: DataFileReader, package: PackageData):
        self._fs, self._reader, self._package = fs, reader, package

    def bundled(self) -> tuple[str, ...]:
        return tuple(name.removesuffix(PROFILE_SUFFIX) for name in self._package.files_in()
                     if name.endswith(PROFILE_SUFFIX))

    def testing_presets(self) -> dict[str, Any]:
        return self._documents(PRESETS)

    def language_presets(self) -> dict[str, Any]:
        return self._documents(LANGUAGES)

    def _documents(self, folder: str) -> dict[str, Any]:
        found: dict[str, Any] = {}
        for name in self._package.files_in(folder):
            if name.endswith(PROFILE_SUFFIX):
                try:
                    found[name.removesuffix(PROFILE_SUFFIX)] = self._reader.parse(
                        self._package.read_text(f"{folder}/{name}"))
                except (OSError, UnicodeDecodeError, DataFileError) as e:
                    raise InvalidArchitecture(f"{folder}/{name}", [f"cannot read the preset: {e}"]) from e
        return found

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        name = _name(source)
        try:
            text = self._package.read_text(name) if source.bundled else self._fs.read_text(Path(source.location))
        except (OSError, UnicodeDecodeError) as e:
            raise InvalidArchitecture(name, [f"cannot read the file: {getattr(e, 'strerror', None) or e}"]) from e
        try:
            document = self._reader.parse(text, json_syntax=name.endswith(".json"))
        except DataFileError as e:
            raise InvalidArchitecture(name, e.problems) from e
        return ArchitectureDocument(name, document)

    def profile_text(self, source: ArchitectureSource) -> str:
        if source.bundled:
            return self.read_text(source, _name(source))
        try:
            return self._fs.read_text(Path(source.location))
        except UnicodeDecodeError as e:
            raise InvalidArchitecture(source.location, ["cannot read the file: it is not valid UTF-8 text"]) from e
        except OSError as e:
            raise InvalidArchitecture(source.location, [f"cannot read the file: {e.strerror or e}"]) from e

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        if source.bundled:
            return self._package.is_file(relative)
        return self._fs.is_file(Path(source.location).parent / relative)

    def files_under(self, source: ArchitectureSource, relative: str) -> tuple[str, ...]:
        if source.bundled:
            return tuple(self._package.files_below(relative))
        return tuple(self._fs.files_below(Path(source.location).parent / relative))

    def read_bytes(self, source: ArchitectureSource, relative: str) -> bytes:
        try:
            if source.bundled:
                return self._package.read_bytes(relative)
            return self._fs.read_bytes(Path(source.location).parent / relative)
        except OSError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {e.strerror or e}"]) from e

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        try:
            if source.bundled:
                return self._package.read_text(relative)
            return self._fs.read_text(Path(source.location).parent / relative)
        except UnicodeDecodeError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': it is not valid UTF-8 text"]) from e
        except OSError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {e.strerror or e}"]) from e


def _name(source: ArchitectureSource) -> str:
    return source.location + PROFILE_SUFFIX if source.bundled else source.location
