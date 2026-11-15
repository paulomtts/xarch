from __future__ import annotations

from xarch.kernel.logic.placement import Place
from xarch.kernel.logic.source import Import, Unparsable
from xarch.kernel.logic.testing import TierView
from xarch.modules.rules.application.logic import enforcement
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import (
    AppChecked,
    ApproximateView,
    CheckApp,
    CheckAppResult,
    CheckImports,
    CheckResult,
    CoveringTest,
    DriftView,
    EnforcementView,
    ExcludedView,
    Fake,
    FindingView,
    ImportsChecked,
    InPart,
    InStructure,
    InTests,
    Locate,
    Located,
    LocateResult,
    NearestView,
    NotADirectory,
    Outside,
    PartShown,
    ReachView,
    Support,
    TierInfoView,
    Ungoverned,
    Untested,
    WhereAnswer,
)
from xarch.modules.rules.domain.errors import OutsideProject, RootMissing, Unreadable
from xarch.modules.rules.domain.values import (
    Enforcement,
    FakePlace,
    PartAt,
    PartInfo,
    PartPlace,
    Placed,
    StructurePlace,
    SuitePlace,
    UngovernedPlace,
)


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService, app: AppCheckService):
        self._service, self._locator, self._app = service, locator, app

    def check_app(self, cmd: CheckApp) -> CheckAppResult:
        """The whole check of an app; a root or tests folder that is no folder is refused."""
        try:
            checked = self._app.check(cmd.root, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        return AppChecked(checked.violations, _enforcement(checked.enforcement), dict(checked.profile.hints),
                          passed(checked.violations, checked.enforcement.strict, cmd.strict))

    def check(self, cmd: CheckImports) -> CheckResult:
        try:
            checked = self._service.check(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        return ImportsChecked(checked.violations, _enforcement(checked.enforcement))

    def locate(self, cmd: Locate) -> LocateResult:
        """A path outside the project is refused with why."""
        try:
            return Located(_where(self._locator.locate(cmd)))
        except OutsideProject as e:
            return Outside(e.reason)


class ReaderController:
    """Reads source text with the reader of the app's language, for a module that holds source as data, such as spec
    its examples: it answers in kernel values, so that such a module reads through it without importing rules. It
    needs no profile, so it is built before the modules that read profiles."""

    def __init__(self, reading: SourceReadService):
        self._reading = reading

    def imports(self, text: str) -> tuple[Import, ...] | Unparsable:
        """What a text that is in no file imports, in order; one that does not parse comes back as where and why."""
        try:
            return self._reading.imports(text)
        except Unreadable as e:
            return e.found


def _enforcement(state: Enforcement) -> EnforcementView:
    return EnforcementView(
        state.origin, state.ungoverned, tuple(enforcement.folders(state.ungoverned)),
        tuple(DriftView("/".join(d.path), d.state) for d in state.init_files), state.skipped, state.dynamic,
        state.weak, tuple(FindingView(f.key, enforcement.detail(f.item)) for f in state.strict),
        tuple(ExcludedView(enforcement.excluded_folder(state.app, e), e.reason) for e in state.excluded),
        state.language, tuple(ApproximateView(a.address, a.fact, a.note or "",
                                              enforcement.approximation(a.address, a.fact, a.note or ""))
                              for a in state.approximate))


def _where(found: Placed) -> WhereAnswer:
    match found:
        case PartPlace():
            return InPart(found.found.shown, found.found.exists, _part(found.place, found.info, found.singular),
                          _reaches(found.reaches), found.may_import_text, found.libraries, found.forbidden,
                          _tested(found))
        case StructurePlace():
            return InStructure(found.found.shown, found.found.exists, _nearest(found.nearest))
        case UngovernedPlace():
            return Ungoverned(found.found.shown, found.found.exists, _nearest(found.nearest), found.closed_tree,
                              found.note)
        case SuitePlace():
            kind = InTests if found.test else Support
            tier = found.tier
            mirrors = (_part(found.place, found.info, found.singular)
                       if found.place is not None and found.info is not None else None)
            return kind(found.found.shown, found.found.exists, mirrors, _reaches(found.reaches),
                        found.may_import_text, tier.types_only if tier is not None else (), found.forbidden,
                        _tier(tier) if tier is not None else None, found.may_use_fakes, found.fakes_path,
                        found.test_code_from, found.note)
        case FakePlace():
            return Fake(found.found.shown, found.found.exists, found.fakes_path, found.test_code_from, found.note)


def _part(place: Place, info: PartInfo, singular: str) -> PartShown:
    return PartShown(place.part or "", info.shown, place.instance or "", singular, info.role, info.litmus)


def _reaches(reaches: tuple[PartAt, ...]) -> tuple[ReachView, ...]:
    return tuple(ReachView(r.target.part, r.target.scope, r.folder, r.path) for r in reaches)


def _nearest(nearest: tuple[PartAt, ...]) -> tuple[NearestView, ...]:
    return tuple(NearestView(n.target.part, n.folder, n.path) for n in nearest)


def _tier(tier: TierView) -> TierInfoView:
    return TierInfoView(tier.name, tier.proves, tier.may_touch, tier.litmus)


def _tested(found: PartPlace) -> CoveringTest | Untested | None:
    if found.tier is not None:
        return CoveringTest(_tier(found.tier), found.test_folder, found.test_file, found.test_folder + found.test_file)
    return Untested(found.untested) if found.untested else None
