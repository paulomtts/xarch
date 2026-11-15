from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.services.scaffolding import Scaffolding
from xarch.modules.scaffold.contract import Init, New, NewResult, Refused, Scaffolded


class ScaffoldController:
    def __init__(self, service: Scaffolding):
        self._service = service

    def init(self, cmd: Init) -> Scaffolded:
        return Scaffolded(self._service.init(cmd.root, cmd.profile))

    def new(self, cmd: New) -> NewResult:
        """Every refusal of the service carries its reason."""
        try:
            report = self._service.new(cmd.root, cmd.kind, cmd.name, cmd.profile)
        except DomainError as e:
            return Refused(e.reason)
        return Scaffolded(report)
