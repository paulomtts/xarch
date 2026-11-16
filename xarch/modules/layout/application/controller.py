from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.layout.contract import CheckStructure, StructureRefused, StructureResult


class LayoutController:
    def __init__(self, service: StructureCheckService):
        self._service = service

    def check(self, cmd: CheckStructure) -> StructureResult:
        """A profile that cannot give its skeleton is refused with why."""
        try:
            return self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except DomainError as e:
            return StructureRefused(e.reason)
