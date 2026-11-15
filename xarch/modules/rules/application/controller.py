from __future__ import annotations

from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.contract import (
    CheckImports,
    CheckResult,
    ImportsChecked,
    Locate,
    Located,
    LocateResult,
    NotADirectory,
    Outside,
)
from xarch.modules.rules.domain.errors import OutsideProject, RootMissing


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService):
        self._service, self._locator = service, locator

    def check(self, cmd: CheckImports) -> CheckResult:
        try:
            found, enforcement = self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        return ImportsChecked(tuple(found), enforcement)

    def locate(self, cmd: Locate) -> LocateResult:
        """A path outside the project is refused with why."""
        try:
            return Located(self._locator.locate(cmd))
        except OutsideProject as e:
            return Outside(e.reason)
