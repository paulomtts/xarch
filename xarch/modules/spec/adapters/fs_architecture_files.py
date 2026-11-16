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
        text = _text(self._folder(source), self._file(source), name, "the file")
        try:
            document = self._reader.parse(text, json_syntax=name.endswith(".json"))
        except DataFileError as e:
            raise InvalidArchitecture(name, e.problems) from e
        return ArchitectureDocument(name, document)

    def profile_text(self, source: ArchitectureSource) -> str:
        return _text(self._folder(source), self._file(source), _name(source), "the file")

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        return self._folder(source).is_file(relative)

    def files_under(self, source: ArchitectureSource, relative: str) -> tuple[str, ...]:
        return tuple(self._folder(source).files_below(relative))

    def read_bytes(self, source: ArchitectureSource, relative: str) -> bytes:
        try:
            return self._folder(source).read_bytes(relative)
        except OSError as e:
            raise InvalidArchitecture(_name(source), [f"cannot read '{relative}': {e.strerror or e}"]) from e

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        return _text(self._folder(source), relative, _name(source), f"'{relative}'")

    def _folder(self, source: ArchitectureSource) -> PackageData | _Folder:
        """The folder an architecture's files are named from: the package data for a bundled one, else the folder
        holding its file."""
        return self._package if source.bundled else _Folder(self._fs, Path(source.location).parent)

    def _file(self, source: ArchitectureSource) -> str:
        """The architecture's own file, named from its folder."""
        return _name(source) if source.bundled else Path(source.location).name


class _Folder:
    """A folder on disk, read by paths relative to it, as the package data is read."""

    def __init__(self, fs: FileSystem, folder: Path):
        self._fs, self._path = fs, folder

    def is_file(self, relative: str) -> bool:
        return self._fs.is_file(self._path / relative)

    def files_below(self, relative: str) -> list[str]:
        return self._fs.files_below(self._path / relative)

    def read_bytes(self, relative: str) -> bytes:
        return self._fs.read_bytes(self._path / relative)

    def read_text(self, relative: str) -> str:
        return self._fs.read_text(self._path / relative)


def _text(folder: PackageData | _Folder, relative: str, name: str, what: str) -> str:
    """The text of the file at relative in folder; raises InvalidArchitecture, for the file called name, saying what
    cannot be read and why."""
    try:
        return folder.read_text(relative)
    except UnicodeDecodeError as e:
        raise InvalidArchitecture(name, [f"cannot read {what}: it is not valid UTF-8 text"]) from e
    except OSError as e:
        raise InvalidArchitecture(name, [f"cannot read {what}: {e.strerror or e}"]) from e


def _name(source: ArchitectureSource) -> str:
    return source.location + PROFILE_SUFFIX if source.bundled else source.location
