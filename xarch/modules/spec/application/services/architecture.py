from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.domain.architecture_file import parse_architecture, source_of
from xarch.modules.spec.domain.values import Architecture


class ArchitectureService:
    def __init__(self, files: ArchitectureFiles):
        self._files = files

    def bundled(self) -> tuple[str, ...]:
        return self._files.bundled()

    def load(self, location: str | Path) -> Architecture:
        """The architecture in a bundled file, by name, or in a file at a path; raises InvalidArchitecture."""
        source = source_of(location, self._files.bundled())                                     # decide
        raw = self._files.read(source)                                                          # load
        return parse_architecture(raw.document, raw.source, lambda relative: self._files.has_file(source, relative))
