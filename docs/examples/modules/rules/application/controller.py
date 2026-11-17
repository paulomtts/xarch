from __future__ import annotations

from app.modules.rules.application.services.app_check import AppCheckService
from app.modules.rules.contract import CheckApp, CheckAppResult, CheckRefused, ChecksCannotRun
from app.modules.rules.domain.errors import NoProfile, ProfileUnusable, SourceUnreadable


class RulesController:
    def __init__(self, service: AppCheckService):
        self._service = service

    def check(self, cmd: CheckApp) -> CheckAppResult:
        try:
            return self._service.check(cmd.root, cmd.profile)
        except (NoProfile, ProfileUnusable) as e:
            return CheckRefused(e.reason)
        except SourceUnreadable as e:
            return ChecksCannotRun((e.reason,))
