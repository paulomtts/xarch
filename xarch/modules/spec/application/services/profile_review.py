from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.application.logic.profile_view import view
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.own_checks import OwnChecks
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.contract import CHECKS, EXAMPLES, LOAD, Problem, ProfileChecked, ProfileViewed
from xarch.modules.spec.domain.errors import InvalidArchitecture


class ProfileReviewService:
    """Looks at a profile without an app: validates it, or shows it. The profile is the one asked for (a bundled name
    or a path), else the one configured for the project holding the app folder."""

    def __init__(self, selection: ProfileSelectionService, architectures: ArchitectureService,
                 files: ArchitectureFiles, own: OwnChecks):
        self._selection, self._architectures, self._files, self._own = selection, architectures, files, own

    def check(self, app: Path, target: str | None) -> ProfileChecked:
        """What validating the profile found: every problem the loader found when it does not load, else what its
        examples import that their part may not and what its own checks find against their examples, with how many
        files it points to, how many checks it writes itself and where it comes from; raises NoProfile or
        UnknownProfile."""
        location = self._selection.location(app, target)
        try:
            self._architectures.load(location)
        except InvalidArchitecture as e:
            return ProfileChecked(location, tuple(Problem(LOAD, text) for text in e.problems), 0, None)
        files = self._architectures.pointed(location)
        held = self._own.held(location, app.name)
        problems = (*(Problem(EXAMPLES, text) for text in self._architectures.check_examples(location)),
                    *(Problem(CHECKS, text) for text in held.problems))
        return ProfileChecked(location, problems, len(files), self._architectures.origin(location), held.checks)

    def view(self, app: Path, target: str | None) -> ProfileViewed:
        """The profile's folder tree and import table; raises NoProfile, UnknownProfile or InvalidArchitecture."""
        location = self._selection.location(app, target)
        architecture = self._architectures.load(location)
        tree, imports = view(architecture)
        return ProfileViewed(location, architecture.name, tree, imports, source_of(location, self._files.bundled()).bundled)
