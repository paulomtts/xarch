from __future__ import annotations

from typing import Any, Protocol

from xarch.modules.spec.domain.values import ArchitectureDocument, ArchitectureSource


class ArchitectureFiles(Protocol):
    """Architecture files: the ones bundled with xarch, and any on disk."""

    def bundled(self) -> tuple[str, ...]:
        """The names of the bundled architectures, e.g. ("cli", "web")."""
        ...

    def testing_presets(self) -> dict[str, Any]:
        """The documents of the presets a profile may name under `testing`, by name, e.g. {"pytest": {...}}: the
        same mapping a profile writes out, shipped as data with xarch."""
        ...

    def read(self, source: ArchitectureSource) -> ArchitectureDocument:
        """The file, parsed but not validated; raises InvalidArchitecture if it cannot be read or parsed."""
        ...

    def has_file(self, source: ArchitectureSource, relative: str) -> bool:
        """Whether a file exists at relative, a path from the folder holding the architecture file."""
        ...

    def files_under(self, source: ArchitectureSource, relative: str) -> tuple[str, ...]:
        """Every file below the folder at relative, a path from the folder holding the architecture file, as its path
        in that folder written with `/`, sorted; empty when there is no such folder or it holds no file."""
        ...

    def read_bytes(self, source: ArchitectureSource, relative: str) -> bytes:
        """The bytes of the file at relative; raises InvalidArchitecture if it cannot be read."""
        ...

    def read_text(self, source: ArchitectureSource, relative: str) -> str:
        """The text of the file at relative, a path from the folder holding the architecture file; raises
        InvalidArchitecture if it cannot be read."""
        ...
