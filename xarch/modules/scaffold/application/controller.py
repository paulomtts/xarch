from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.services.scaffolding import Scaffolding
from xarch.modules.scaffold.contract import Init, NewModule, NewModuleResult, Refused, Scaffolded


class ScaffoldController:
    def __init__(self, service: Scaffolding):
        self._service = service

    def init(self, cmd: Init) -> Scaffolded:
        return Scaffolded(self._service.init(cmd.root, cmd.profile))

    def new_module(self, cmd: NewModule) -> NewModuleResult:
        try:
            report = self._service.new_module(cmd.root, cmd.name, cmd.profile)
        except DomainError as e:                                     # every refusal carries its reason
            return Refused(e.reason)
        return Scaffolded(report)
