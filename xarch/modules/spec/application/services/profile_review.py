from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.application.logic.profile_files import pointed_files
from xarch.modules.spec.application.logic.profile_in_force import choose
from xarch.modules.spec.application.logic.profile_view import view
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import CheckProfile, Problem, ProfileChecked, ProfileViewed, ViewProfile
from xarch.modules.spec.domain.errors import InvalidArchitecture

LOAD = "load"
EXAMPLES = "examples"


class ProfileReview:
    """Looks at a profile without an app: validates it, or shows its folder tree and import table. The profile is the
    one asked for (a bundled name or a path), else the one configured for the project holding the app folder."""

    def __init__(self, settings: Settings, architectures: ArchitectureService, files: ArchitectureFiles):
        self._settings, self._architectures, self._files = settings, architectures, files

    def check(self, cmd: CheckProfile) -> ProfileChecked:
        """Raises NoProfile or UnknownProfile; a profile that does not load is reported, not raised."""
        location = self._location(cmd.app, cmd.target)
        try:
            architecture = self._architectures.load(location)
        except InvalidArchitecture as e:
            return ProfileChecked(location, tuple(Problem(LOAD, problem) for problem in e.problems), 0, None)
        source = source_of(location, self._files.bundled())
        files = pointed_files(architecture, lambda folder: self._files.files_under(source, folder))
        found = [Problem(EXAMPLES, problem) for problem in self._architectures.check_examples(location)]
        return ProfileChecked(location, tuple(found), len(files), self._architectures.origin(location))

    def view(self, cmd: ViewProfile) -> ProfileViewed:
        """Raises NoProfile, UnknownProfile or InvalidArchitecture."""
        location = self._location(cmd.app, cmd.target)
        architecture = self._architectures.load(location)
        tree, imports = view(architecture)
        return ProfileViewed(location, architecture.name, tree, imports, source_of(location, self._files.bundled()).bundled)

    def _location(self, app: Path, target: str | None) -> str:
        configured = None if target is not None else self._settings.configured_profile(app)
        return choose(target, configured, self._files.bundled())
