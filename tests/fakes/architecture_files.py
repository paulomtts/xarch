"""In-memory implementation of spec's ArchitectureFiles port. Not an adapter: a test double only."""
from __future__ import annotations

from typing import Any

from tests.modules.spec.format_files import KEYS_DOCUMENT
from tests.modules.spec.languages import PYTHON_DOCUMENT
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import PROFILE_SUFFIX, ArchitectureDocument, ArchitectureSource


class FakeArchitectureFiles:
    """Satisfies spec's ArchitectureFiles: documents already parsed, bundled by name or at a path, and the text of
    the files beside them by their relative path (text, or bytes for one that is not text), and the presets of
    `testing` by name, the data files of the languages by name (Python's, unless given), and the document of the data
    file of the format's texts (the shipped one, unless given). A document it does not hold cannot be read."""

    def __init__(self, bundled: dict[str, Any] | None = None, files: dict[str, Any] | None = None,
                 texts: dict[str, str | bytes] | None = None, presets: dict[str, Any] | None = None,
                 languages: dict[str, Any] | None = None, keys: Any = None):
        self._bundled, self._files, self._texts = dict(bundled or {}), dict(files or {}), dict(texts or {})
        self._presets = dict(presets or {})
        self._languages = {"python": PYTHON_DOCUMENT} if languages is None else dict(languages)
        self._keys = KEYS_DOCUMENT if keys is None else keys

    def testing_presets(self) -> dict[str, Any]:
        return dict(self._presets)

    def language_presets(self) -> dict[str, Any]:
        return dict(self._languages)

    def format_keys(self) -> Any:
        return self._keys

    def bundled(self) -> tuple[str, ...]:
        return tuple(sorted(self._bundled))

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        documents = self._bundled if source.bundled else self._files
        if source.location not in documents:
            raise InvalidArchitecture(source.location, ["cannot read the file: no such file"])
        return ArchitectureDocument(source.location, documents[source.location])

    def profile_text(self, source: ArchitectureSource) -> str:
        return self.read_text(source, f"{source.location}{PROFILE_SUFFIX}" if source.bundled else source.location)

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        return relative in self._texts

    def files_under(self, source: ArchitectureSource, relative: str) -> tuple[str, ...]:
        prefix = relative.rstrip("/") + "/"
        return tuple(sorted(name.removeprefix(prefix) for name in self._texts if name.startswith(prefix)))

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        found = self.read_bytes(source, relative)
        return found if isinstance(found, str) else found.decode("utf-8")

    def read_bytes(self, source: ArchitectureSource, relative: str) -> bytes:
        if relative not in self._texts:
            raise InvalidArchitecture(source.location, [f"cannot read '{relative}': no such file"])
        found = self._texts[relative]
        return found.encode("utf-8") if isinstance(found, str) else found
