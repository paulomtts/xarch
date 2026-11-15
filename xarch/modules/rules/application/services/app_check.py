from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.domain.values import Enforcement


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, profiles: Profiles):
        self._source, self._structure, self._profiles = source, structure, profiles

    def check(self, root: Path, profile: str, tests: Path | None, strict: bool) -> tuple[list[Violation], Enforcement,
                                                                                          dict[str, str], bool]:
        """The violations, the enforcement, the profile's hints by rule id, and whether the check passes; raises
        RootMissing when the app folder or the tests folder is no folder."""
        package = root.absolute().resolve().name
        found, enforcement = self._source.check(root, package, profile, tests)
        found = found + self._structure.violations(root, package, profile, tests)
        return found, enforcement, dict(self._profiles.profile(profile).hints), passed(found, enforcement.strict, strict)
