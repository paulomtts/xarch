from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from xarch.kernel.source import Import
from xarch.modules.spec.application.logic.docs_files import doc_files
from xarch.modules.spec.application.logic.example_imports import (
    Read,
    checked_examples,
    example_problems,
    shipped_problems,
)
from xarch.modules.spec.application.logic.file_types import file_types_of
from xarch.modules.spec.application.logic.language_file import first_language, language_of
from xarch.modules.spec.application.logic.looseness import origin_of
from xarch.modules.spec.application.logic.profile_file import parse_profile, source_of
from xarch.modules.spec.application.logic.profile_files import pointed_files
from xarch.modules.spec.application.logic.profile_listing import listing, referenced
from xarch.modules.spec.application.logic.project_files import entries, project_files, with_app
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.example_reader import ExampleReader
from xarch.modules.spec.application.ports.runtime import Runtime
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.published import EXAMPLE_APP, DocFile, Origin, ProjectFile
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource, FileType, Language


class ArchitectureService:
    def __init__(self, files: ArchitectureFiles, runtime: Runtime, reader: ExampleReader):
        self._files, self._runtime, self._reader = files, runtime, reader
        self._bundled: dict[str, tuple[ArchitectureSource, Architecture]] = {}
        self._testing: dict[str, Any] | None = None
        self._languages: dict[str, Language] | None = None
        self._types: dict[str, FileType] | None = None

    def load(self, location: str | Path) -> Architecture:
        """The architecture in a bundled file, by name, or in a file at a path; raises InvalidArchitecture."""
        return self._load(location)[1]

    def check_examples(self, location: str | Path) -> tuple[str, ...]:
        """Every import of the architecture's examples that its rules forbid and every example in no part; raises
        InvalidArchitecture if the file cannot be loaded or an example read."""
        source, architecture = self._load(location)
        return tuple(example_problems(architecture, self._reads(architecture, self._example_texts(source, architecture))))

    def placed(self, location: str | Path) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
        """The files placement is held to, each its path below the app, the part it lies in and its code: the clean
        ones (the docs' examples lying in a part, then `evals.placement.examples.clean`) and the flagged ones; raises
        InvalidArchitecture if the file cannot be loaded or an example read."""
        source, architecture = self._load(location)
        texts = self._example_texts(source, architecture)
        docs = [(name, example.part, texts[name]) for name, example in architecture.examples.items() if example.part]
        flagged, clean = architecture.placed
        return (docs + [(path, self._part(architecture, path), code) for path, code in clean],
                [(path, self._part(architecture, path), code) for path, code in flagged])

    def imports(self, text: str) -> tuple[Import, ...]:
        """The imports of a text, as the reader of the app's language reads them; none when it does not parse."""
        found = self._reader.imports(text)
        return found if isinstance(found, tuple) else ()

    @staticmethod
    def _part(architecture: Architecture, path: str) -> str:
        return architecture.place_of(tuple(path.split("/"))).part or ""

    def pointed(self, location: str | Path) -> tuple[str, ...]:
        """Every file next to the profile that it points to, as pointed_files lists them; raises InvalidArchitecture."""
        source, architecture = self._load(location)
        return pointed_files(architecture, {entry.source: self._files.files_under(source, entry.source)
                                            for entry in architecture.files if entry.folder})

    def parse_copy(self, document: Any, source: str, outputs: Mapping[str, bytes]) -> Architecture:
        """The architecture a profile about to be written describes, its files being outputs, by their path from it;
        raises InvalidArchitecture."""
        return parse_profile(document, source, tuple(outputs), self._presets(), self._files.bundled(),
                             self._language_presets())

    def docs(self, location: str | Path) -> list[DocFile]:
        """The project docs the architecture declares, by their path below the docs root, each filled from its
        template; raises InvalidArchitecture or InvalidTemplate. A bundled architecture's examples must also pass the
        example check."""
        source, architecture = self._load(location)
        texts = {doc.source: self._files.read_text(source, doc.source) for doc in architecture.docs if doc.source}
        examples = self._example_texts(source, architecture)
        tier_examples = self._tier_example_texts(source, architecture)
        problems = shipped_problems(architecture, self._reads(architecture, examples), source.bundled)
        if problems:
            raise InvalidArchitecture(source.location, problems)
        return list(doc_files(architecture, texts, examples, tier_examples, file_types=self._file_types()))

    def files(self, location: str | Path, app: str, presets: bool = True) -> list[ProjectFile]:
        """The project files the architecture declares for an app folder called app, each filled from its template
        unless it says otherwise, a folder entry as every file under its folder but those the language's tools compile
        (unless presets is off, which leaves those unread); raises InvalidArchitecture."""
        source, architecture = self._load(location)
        kept = entries(architecture, presets)
        listing = {file.source: [name for name in self._files.files_under(source, file.source)
                                 if not architecture.language.compiled(name)] for file in kept if file.folder}
        contents = {file.source: self._files.read_bytes(source, file.source) for file in kept if not file.folder}
        contents.update({f"{folder}/{name}": self._files.read_bytes(source, f"{folder}/{name}")
                         for folder, names in listing.items() for name in names})
        return list(project_files(replace(architecture, files=kept), contents, app, source.location, listing))

    def origin(self, location: str | Path) -> Origin:
        """Where the architecture comes from, the guards it leaves off and, for a custom file, how it is looser than
        the bundled architecture it resembles; raises InvalidArchitecture."""
        source, architecture = self._load(location)
        others = {} if source.bundled else {name: self.load(name) for name in self._files.bundled()}
        return origin_of(source.location, architecture, source.bundled, others)

    def _example_texts(self, source: ArchitectureSource, architecture: Architecture) -> dict[str, str]:
        return {name: self._files.read_text(source, example.file) for name, example in architecture.examples.items()}

    def _reads(self, architecture: Architecture, texts: Mapping[str, str]) -> dict[str, Read]:
        """Each example the check reads, as the reader of the app's language reads its text, by name."""
        return {example.name: self._reader.imports(texts[example.name]) for example in checked_examples(architecture)}

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

    def _file_types(self) -> dict[str, FileType]:
        """The kinds of file the docs quote besides the language of the app, read from their data file once."""
        if self._types is None:
            self._types = file_types_of(self._files.file_types())
        return self._types

    def default_language(self) -> Language:
        """The language of an app whose profile names none: the first the data files of the languages give, by name."""
        found = self._language_presets()
        return found.get(first_language(found), Language())

    def _language_presets(self) -> dict[str, Language]:
        """The languages xarch ships, read once, each with the names only the runtime knows."""
        if self._languages is None:
            self._languages = {
                name: replace(language, standard_names=self._runtime.standard_library(language.standard),
                              builtin_names=self._runtime.builtin_names(language.standard),
                              reserved_names=self._runtime.reserved_words(language.standard))
                for name, document in self._files.language_presets().items()
                for language in [language_of(name, document)]}
        return self._languages

    def _load(self, location: str | Path) -> tuple[ArchitectureSource, Architecture]:
        """The source and its architecture; a bundled one is read once, since it cannot change while xarch runs."""
        source = source_of(location, self._files.bundled())
        if source.bundled and source.location in self._bundled:
            return self._bundled[source.location]
        raw = self._files.read(source)
        named, folders = referenced(raw.document)
        files = listing((name for name in named if self._files.has_file(source, name)),
                        {folder: self._files.files_under(source, folder) for folder in folders})
        loaded = source, parse_profile(raw.document, raw.source, files, self._presets(), self._files.bundled(),
                                              self._language_presets())
        if source.bundled:
            self._bundled[source.location] = loaded
        return loaded
