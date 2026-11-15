from __future__ import annotations

from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.layout.contract import CheckStructure, StructureChecked


class LayoutController:
    def __init__(self, service: StructureCheckService):
        self._service = service

    def check(self, cmd: CheckStructure) -> StructureChecked:
        return StructureChecked(tuple(self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)))
