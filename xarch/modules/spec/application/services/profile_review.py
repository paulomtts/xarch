from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.layout_walk import docs_name
from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.application.logic.profile_view import view
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.contract import EXAMPLES, LOAD, Problem, ProfileChecked, ProfileViewed
from xarch.modules.spec.domain.errors import InvalidArchitecture


class ProfileReviewService:
    """Looks at a profile without an app: validates it, or shows it. The profile is the one asked for (a bundled name
    or a path), else the one configured for the project holding the app folder."""

    def __init__(self, selection: ProfileSelectionService, architectures: ArchitectureService,
                 files: ArchitectureFiles):
        self._selection, self._architectures, self._files = selection, architectures, files

    def check(self, app: Path, target: str | None, against: str | None = None) -> ProfileChecked:
        """What validating the profile found: every problem the loader found when it does not load, else what its
        examples import that their part may not, with how many files it points to and where it comes from, compared
        with the profile against names when it is given, which is read only once the profile loads; raises NoProfile,
        UnknownProfile or AgainstUnloaded."""
        location = self._selection.location(app, target)
        try:
            self._architectures.load(location)
        except InvalidArchitecture as e:
            return ProfileChecked(location, tuple(Problem(LOAD, text) for text in e.problems), 0, None)
        files = self._architectures.pointed(location)
        problems = tuple(Problem(EXAMPLES, text) for text in self._architectures.check_examples(location))
        return ProfileChecked(location, problems, len(files), self._architectures.origin(location, against))

    def view(self, app: Path, target: str | None) -> ProfileViewed:
        """The profile's folder tree and import table; raises NoProfile, UnknownProfile or InvalidArchitecture."""
        location = self._selection.location(app, target)
        architecture = self._architectures.load(location)
        tree, imports = view(architecture)
        return ProfileViewed(location, architecture.name, tree, imports, source_of(location, self._files.bundled()).bundled,
                             tuple(docs_name(architecture, part) for part in architecture.parts.values() if part.optional),
                             architecture.counterparts,
                             tuple((name, entry) for name, part in architecture.parts.items()
                                   for entry in part.imports_accepted))
