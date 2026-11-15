from __future__ import annotations

from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.contract import (
    AppChecked,
    AtView,
    CheckApp,
    CheckAppResult,
    CheckImports,
    CheckResult,
    DriftView,
    EnforcementView,
    ExcludedView,
    FindingView,
    ImportsChecked,
    Locate,
    Located,
    LocateResult,
    LoosenedView,
    NearestView,
    NotADirectory,
    OriginView,
    Outside,
    ReachView,
    TierInfoView,
    WeakView,
    WhereView,
)
from xarch.modules.rules.domain.errors import OutsideProject, RootMissing
from xarch.modules.rules.domain.values import Enforcement, Where


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService, app: AppCheckService):
        self._service, self._locator, self._app = service, locator, app

    def check_app(self, cmd: CheckApp) -> CheckAppResult:
        """The whole check of an app; a root or tests folder that is no folder is refused."""
        try:
            found, enforcement, hints, ok = self._app.check(cmd.root, cmd.profile, cmd.tests, cmd.strict)
        except RootMissing as e:
            return NotADirectory(e.root)
        return AppChecked(tuple(found), _enforcement(enforcement), hints, ok)

    def check(self, cmd: CheckImports) -> CheckResult:
        try:
            found, enforcement = self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        return ImportsChecked(tuple(found), _enforcement(enforcement))

    def locate(self, cmd: Locate) -> LocateResult:
        """A path outside the project is refused with why."""
        try:
            return Located(_where(self._locator.locate(cmd)))
        except OutsideProject as e:
            return Outside(e.reason)


def _enforcement(state: Enforcement) -> EnforcementView:
    origin = state.origin
    return EnforcementView(
        OriginView(origin.location, origin.bundled, origin.closest, origin.guards_off, origin.baseline_off,
                   tuple(LoosenedView(item.key, item.part, item.what, item.sentence) for item in origin.looser)),
        state.ungoverned, tuple(DriftView(d.file, d.state) for d in state.init_files),
        tuple(AtView(a.file, a.line) for a in state.skipped), tuple(AtView(a.file, a.line) for a in state.dynamic),
        tuple(WeakView(w.rule, w.file, w.line, w.message, w.fix) for w in state.weak),
        tuple(FindingView(f.key, f.detail) for f in state.strict),
        tuple(ExcludedView(e.folder, e.reason) for e in state.excluded))


def _where(found: Where) -> WhereView:
    tier = found.tier
    return WhereView(
        found.kind, found.path, found.exists, found.part, found.role, found.litmus, found.folder, found.instance,
        found.singular, tuple(ReachView(r.part, r.scope, r.folder, r.path) for r in found.may_import),
        found.may_import_text, found.libraries, found.forbidden,
        TierInfoView(tier.name, tier.proves, tier.may_touch, tier.litmus) if tier is not None else None,
        found.untested, found.test_folder, found.test_file,
        tuple(NearestView(n.part, n.folder, n.path) for n in found.nearest), found.closed_tree, found.may_use_fakes,
        found.fakes_path, found.types_only, found.test_code_from, found.note)
