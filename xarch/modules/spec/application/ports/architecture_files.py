from __future__ import annotations

from typing import Protocol

from xarch.modules.spec.domain.values import ArchitectureDocument, ArchitectureSource


class ArchitectureFiles(Protocol):
    """Architecture files: the ones bundled with xarch, and any on disk."""

    def bundled(self) -> tuple[str, ...]:
        """The names of the bundled architectures, e.g. ("cli", "web")."""
        ...

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        """The file, parsed but not validated; raises InvalidArchitecture if it cannot be read or parsed."""
        ...

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        """Whether a file exists at relative, a path from the folder holding the architecture file."""
        ...

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        """The text of the file at relative, a path from the folder holding the architecture file; raises
        InvalidArchitecture if it cannot be read."""
        ...
