from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture, Review

LOAD = "load"
EXAMPLES = "examples"


class ProfileReviewService:
    """Looks at a profile without an app: validates it, or shows it. The profile is the one asked for (a bundled name
    or a path), else the one configured for the project holding the app folder."""

    def __init__(self, selection: ProfileSelectionService, architectures: ArchitectureService,
                 files: ArchitectureFiles):
        self._selection, self._architectures, self._files = selection, architectures, files

    def check(self, app: Path, target: str | None) -> Review:
        """Raises NoProfile or UnknownProfile; a profile that does not load is reviewed with what the loader found."""
        location = self._selection.location(app, target)
        try:
            self._architectures.load(location)
        except InvalidArchitecture as e:
            return Review(location, tuple((LOAD, problem) for problem in e.problems), 0, None)
        files = self._architectures.pointed(location)
        found = tuple((EXAMPLES, problem) for problem in self._architectures.check_examples(location))
        return Review(location, found, len(files), self._architectures.origin(location))

    def view(self, app: Path, target: str | None) -> tuple[str, Architecture, bool]:
        """The location of the profile, its architecture and whether it is bundled; raises NoProfile, UnknownProfile or
        InvalidArchitecture."""
        location = self._selection.location(app, target)
        return location, self._architectures.load(location), source_of(location, self._files.bundled()).bundled
