from __future__ import annotations

from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.rules.application.services.locate import Locator
from xarch.modules.rules.contract import CheckImports, CheckResult, ImportsChecked, Locate, LocateResult, NotADirectory
from xarch.modules.rules.domain.errors import RootMissing


class RulesController:
    def __init__(self, service: ImportCheck, locator: Locator):
        self._service, self._locator = service, locator

    def check(self, cmd: CheckImports) -> CheckResult:
        try:
            found, enforcement = self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        return ImportsChecked(tuple(found), enforcement)

    def locate(self, cmd: Locate) -> LocateResult:
        return self._locator.locate(cmd)
