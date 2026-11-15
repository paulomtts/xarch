"""In-memory implementation of spec's ArchitectureFiles port. Not an adapter: a test double only."""
from __future__ import annotations

from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureDocument, ArchitectureSource


class FakeArchitectureFiles:
    """Satisfies spec's ArchitectureFiles: documents already parsed, bundled by name or at a path, and the text of
    the files beside them by their relative path (text, or bytes for one that is not text). A document it does not
    hold cannot be read."""

    def __init__(self, bundled: dict[str, Any] | None = None, files: dict[str, Any] | None = None,
                 texts: dict[str, str | bytes] | None = None):
        self._bundled, self._files, self._texts = dict(bundled or {}), dict(files or {}), dict(texts or {})

    def bundled(self) -> tuple[str, ...]:
        return tuple(sorted(self._bundled))

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        documents = self._bundled if source.bundled else self._files
        if source.location not in documents:
            raise InvalidArchitecture(source.location, ["cannot read the file: no such file"])
        return ArchitectureDocument(source.location, documents[source.location])

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
