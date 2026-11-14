from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.contract import DocFile, Docs
from xarch.modules.spec.domain.architecture_file import parse_architecture, source_of
from xarch.modules.spec.domain.docs import DOCS_ROOT, doc_files
from xarch.modules.spec.domain.errors import InvalidTemplate
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource


class ArchitectureService:
    def __init__(self, files: ArchitectureFiles):
        self._files = files

    def bundled(self) -> tuple[str, ...]:
        return self._files.bundled()

    def load(self, location: str | Path) -> Architecture:
        """The architecture in a bundled file, by name, or in a file at a path; raises InvalidArchitecture."""
        return self._load(location)[1]

    def docs(self, location: str | Path) -> Docs:
        """The project docs, architecture.md and testing.md filled from the architecture; raises InvalidArchitecture
        or InvalidTemplate."""
        source, architecture = self._load(location)                                             # load
        if architecture.docs_template is None:                                                  # check
            raise InvalidTemplate(source.location, ["the architecture has no `docs: {template: <file>}` to fill"])
        template = self._files.read_text(source, architecture.docs_template)
        entry = architecture.entry
        driver_test = self._files.read_text(source, entry.driver_test) if entry and entry.driver_test else None
        files = doc_files(architecture, template, architecture.docs_template, driver_test)       # act
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in files))

    def _load(self, location: str | Path) -> tuple[ArchitectureSource, Architecture]:
        source = source_of(location, self._files.bundled())                                     # decide
        raw = self._files.read(source)                                                          # load
        return source, parse_architecture(raw.document, raw.source,
                                          lambda relative: self._files.has_file(source, relative))
