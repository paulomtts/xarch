from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.scaffold.contract import (
    InitProject,
    InitResult,
    KindIsAFolder,
    NewInstance,
    NewResult,
    NotInitialized,
    Refused,
    Scaffolded,
)
from xarch.modules.scaffold.domain.errors import FolderMissing, UnknownKind


class ScaffoldController:
    def __init__(self, service: ScaffoldingService):
        self._service = service

    def init(self, cmd: InitProject) -> InitResult:
        """A profile that cannot give the skeleton, or a file that cannot be written, is refused with why."""
        try:
            return Scaffolded(self._service.init(cmd.root, cmd.profile, cmd.cwd))
        except DomainError as e:
            return Refused(e.reason)

    def new(self, cmd: NewInstance) -> NewResult:
        """The folder of a kind given for its word, and a skeleton not there, are refused as what they are; every
        other refusal of the service carries its reason."""
        try:
            return Scaffolded(self._service.new(cmd.root, cmd.kind, cmd.name, cmd.profile))
        except UnknownKind as e:
            return KindIsAFolder(e.kind, e.word) if e.word else Refused(e.reason)
        except FolderMissing as e:
            return NotInitialized(e.folder)
        except DomainError as e:
            return Refused(e.reason)

