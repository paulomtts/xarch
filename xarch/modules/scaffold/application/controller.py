from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.scaffold.contract import Init, New, NewResult, Refused, Report, Scaffolded
from xarch.modules.scaffold.domain.values import CREATED, SKIPPED, UPDATED, Touched


class ScaffoldController:
    def __init__(self, service: ScaffoldingService):
        self._service = service

    def init(self, cmd: Init) -> Scaffolded:
        return Scaffolded(_report(self._service.init(cmd.root, cmd.profile)))

    def new(self, cmd: New) -> NewResult:
        """Every refusal of the service carries its reason."""
        try:
            touched = self._service.new(cmd.root, cmd.kind, cmd.name, cmd.profile)
        except DomainError as e:
            return Refused(e.reason)
        return Scaffolded(_report(touched))


def _report(touched: list[Touched]) -> Report:
    """Each file under what was done to it, in the order the files were reached."""
    return Report(created=[t.path for t in touched if t.done == CREATED],
                  skipped=[t.path for t in touched if t.done == SKIPPED],
                  updated=[t.path for t in touched if t.done == UPDATED])
