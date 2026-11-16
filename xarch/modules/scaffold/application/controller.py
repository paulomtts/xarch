from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.scaffold.contract import Init, InitResult, New, NewResult, Refused, Scaffolded


class ScaffoldController:
    def __init__(self, service: ScaffoldingService):
        self._service = service

    def init(self, cmd: Init) -> InitResult:
        """A profile that cannot give the skeleton, or a file that cannot be written, is refused with why."""
        try:
            return Scaffolded(self._service.init(cmd.root, cmd.profile, cmd.cwd))
        except DomainError as e:
            return Refused(e.reason)

    def new(self, cmd: New) -> NewResult:
        """Every refusal of the service carries its reason."""
        try:
            return Scaffolded(self._service.new(cmd.root, cmd.kind, cmd.name, cmd.profile))
        except DomainError as e:
            return Refused(e.reason)

