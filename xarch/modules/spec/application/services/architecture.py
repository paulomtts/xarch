from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from xarch.modules.spec.application.logic.example_imports import example_problems
from xarch.modules.spec.application.logic.looseness import closest, guards_off, looser
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.contract import DocFile, Docs, Loosened, ProfileOrigin, ProjectFile
from xarch.modules.spec.domain.docs import DOCS_ROOT, doc_files
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.profile_file import parse_profile, source_of
from xarch.modules.spec.domain.project_files import EXAMPLE_APP, project_files, with_app
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource


class ArchitectureService:
    def __init__(self, files: ArchitectureFiles):
        self._files = files
        self._bundled: dict[str, tuple[ArchitectureSource, Architecture]] = {}
        self._testing: dict[str, Any] | None = None

    def load(self, location: str | Path) -> Architecture:
        """The architecture in a bundled file, by name, or in a file at a path; raises InvalidArchitecture."""
        return self._load(location)[1]

    def check_examples(self, location: str | Path) -> tuple[str, ...]:
        """Every import of the architecture's Python examples that its rules forbid and every example in no part; raises
        InvalidArchitecture if the file cannot be loaded or an example read."""
        source, architecture = self._load(location)
        return tuple(example_problems(architecture, self._example_texts(source, architecture)))

    def docs(self, location: str | Path) -> Docs:
        """The project docs the architecture declares, each filled from its template; raises InvalidArchitecture or
        InvalidTemplate. A bundled architecture's examples must also pass the example check."""
        source, architecture = self._load(location)
        texts = {doc.source: self._files.read_text(source, doc.source) for doc in architecture.docs if doc.source}
        examples = self._example_texts(source, architecture)
        tier_examples = self._tier_example_texts(source, architecture)
        problems = example_problems(architecture, examples) if source.bundled else []
        if problems:
            raise InvalidArchitecture(source.location, problems)
        files = doc_files(architecture, texts, examples, tier_examples)
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in files))

    def files(self, location: str | Path, app: str, presets: bool = True) -> tuple[ProjectFile, ...]:
        """The project files the architecture declares for an app folder called app, each filled from its template
        unless it says otherwise, a folder entry as every file under its folder (unless presets is off, which leaves
        those unread); raises InvalidArchitecture."""
        source, architecture = self._load(location)
        entries = [file for file in architecture.files if presets or not file.folder]
        listing = {file.source: self._files.files_under(source, file.source) for file in entries if file.folder}
        contents = {file.source: self._files.read_bytes(source, file.source) for file in entries if not file.folder}
        contents.update({f"{folder}/{name}": self._files.read_bytes(source, f"{folder}/{name}")
                         for folder, names in listing.items() for name in names})
        written = project_files(replace(architecture, files=tuple(entries)), contents, app, source.location, listing)
        return tuple(ProjectFile(w.path, w.content, w.pinned, w.preset) for w in written)

    def origin(self, location: str | Path) -> ProfileOrigin:
        """Where the architecture comes from, the guards it leaves off and, for a custom file, how it is looser than
        the bundled architecture it resembles; raises InvalidArchitecture."""
        source, architecture = self._load(location)
        off = guards_off(architecture)
        if source.bundled:
            return ProfileOrigin(source.location, True, None, off, off, ())
        bundled = {name: self.load(name) for name in self._files.bundled()}
        name = closest(architecture, bundled)
        if name is None:
            return ProfileOrigin(source.location, False, None, off, (), ())
        baseline = guards_off(bundled[name])
        return ProfileOrigin(source.location, False, name, off, tuple(g for g in off if g in baseline),
                             tuple(Loosened(*found) for found in looser(architecture, bundled[name])))

    def _example_texts(self, source: ArchitectureSource, architecture: Architecture) -> dict[str, str]:
        return {name: self._files.read_text(source, example.file) for name, example in architecture.examples.items()}

    def _tier_example_texts(self, source: ArchitectureSource, architecture: Architecture) -> dict[str, str]:
        """A helper is keyed by its file; the app folder's placeholder is filled as the docs' example project has it."""
        texts = {tier.name: self._files.read_text(source, tier.example.file)
                 for tier in architecture.tiers if tier.example is not None}
        texts.update({helper.file: self._files.read_text(source, helper.file)
                      for tier in architecture.tiers for helper in tier.helpers})
        return {key: with_app(text, EXAMPLE_APP) for key, text in texts.items()}

    def _presets(self) -> dict[str, Any]:
        """The `testing` presets, read once: they ship with xarch and cannot change while it runs."""
        if self._testing is None:
            self._testing = self._files.testing_presets()
        return self._testing

    def _load(self, location: str | Path) -> tuple[ArchitectureSource, Architecture]:
        """The source and its architecture; a bundled one is read once, since it cannot change while xarch runs."""
        source = source_of(location, self._files.bundled())
        if source.bundled and source.location in self._bundled:
            return self._bundled[source.location]
        raw = self._files.read(source)
        loaded = source, parse_profile(raw.document, raw.source, lambda relative: self._files.has_file(source, relative),
                                       lambda relative: self._files.files_under(source, relative) or None,
                                       self._presets(), self._files.bundled())
        if source.bundled:
            self._bundled[source.location] = loaded
        return loaded
