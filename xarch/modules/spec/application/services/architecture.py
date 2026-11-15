from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.example_imports import example_problems
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.contract import DocFile, Docs
from xarch.modules.spec.domain.architecture_file import parse_architecture, source_of
from xarch.modules.spec.domain.docs import DOCS_ROOT, doc_files
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource


class ArchitectureService:
    def __init__(self, files: ArchitectureFiles):
        self._files = files
        self._bundled: dict[str, tuple[ArchitectureSource, Architecture]] = {}

    def bundled(self) -> tuple[str, ...]:
        return self._files.bundled()

    def load(self, location: str | Path) -> Architecture:
        """The architecture in a bundled file, by name, or in a file at a path; raises InvalidArchitecture."""
        return self._load(location)[1]

    def check_examples(self, location: str | Path) -> tuple[str, ...]:
        """Every import of the architecture's Python examples that its rules forbid, every example in no part, and
        every tier's Python example test that does not parse; raises InvalidArchitecture if the file cannot be loaded
        or an example read."""
        source, architecture = self._load(location)
        return tuple(example_problems(architecture, self._example_texts(source, architecture),
                                      self._tier_example_texts(source, architecture)))

    def docs(self, location: str | Path) -> Docs:
        """The project docs the architecture declares, each filled from its template; raises InvalidArchitecture or
        InvalidTemplate. A bundled architecture's examples must also pass the example check."""
        source, architecture = self._load(location)
        texts = {doc.source: self._files.read_text(source, doc.source) for doc in architecture.docs if doc.source}
        examples = self._example_texts(source, architecture)
        tier_examples = self._tier_example_texts(source, architecture)
        problems = example_problems(architecture, examples, tier_examples) if source.bundled else []
        if problems:
            raise InvalidArchitecture(source.location, problems)
        files = doc_files(architecture, texts, examples, tier_examples)
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in files))

    def _example_texts(self, source: ArchitectureSource, architecture: Architecture) -> dict[str, str]:
        return {name: self._files.read_text(source, example.file) for name, example in architecture.examples.items()}

    def _tier_example_texts(self, source: ArchitectureSource, architecture: Architecture) -> dict[str, str]:
        """A helper is keyed by its file."""
        texts = {tier.name: self._files.read_text(source, tier.example.file)
                 for tier in architecture.tiers if tier.example is not None}
        texts.update({helper.file: self._files.read_text(source, helper.file)
                      for tier in architecture.tiers for helper in tier.helpers})
        return texts

    def _load(self, location: str | Path) -> tuple[ArchitectureSource, Architecture]:
        """The source and its architecture; a bundled one is read once, since it cannot change while xarch runs."""
        source = source_of(location, self._files.bundled())
        if source.bundled and source.location in self._bundled:
            return self._bundled[source.location]
        raw = self._files.read(source)
        loaded = source, parse_architecture(raw.document, raw.source,
                                            lambda relative: self._files.has_file(source, relative))
        if source.bundled:
            self._bundled[source.location] = loaded
        return loaded
