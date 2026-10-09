from __future__ import annotations

from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.rules.contract import CheckImports, CheckResult, ImportsChecked, NotADirectory
from xarch.modules.rules.domain.errors import RootMissing


class RulesController:
    def __init__(self, service: ImportCheck):
        self._service = service

    def check(self, cmd: CheckImports) -> CheckResult:
        try:
            found = self._service.check(cmd.root, cmd.package, cmd.profile)
        except RootMissing:
            return NotADirectory(cmd.root)
        return ImportsChecked(tuple(found))
