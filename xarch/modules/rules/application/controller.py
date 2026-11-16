from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.placement import Place
from xarch.kernel.logic.source import Import, Unparsable
from xarch.kernel.logic.testing import TierView
from xarch.modules.rules.application.logic import enforcement, explained
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.logic.written import written
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import (
    AppChecked,
    ApproximateView,
    CategoryShown,
    CheckApp,
    CheckAppResult,
    CheckImports,
    CheckResult,
    ChecksShown,
    CoveringTest,
    DriftView,
    EnforcementView,
    ExcludedView,
    ExplainRule,
    ExplainWords,
    Fake,
    FieldShown,
    FindingView,
    ImportsChecked,
    InPart,
    InStructure,
    InTests,
    Locate,
    Located,
    LocateResult,
    NearestView,
    NoRuleShown,
    NotADirectory,
    Outside,
    PartShown,
    ReachView,
    RuleResult,
    RuleShown,
    SlotShown,
    Support,
    TierInfoView,
    Ungoverned,
    UnknownWords,
    Untested,
    WhereAnswer,
    WordLine,
    WordShown,
    WordsResult,
    WordsShown,
)
from xarch.modules.rules.domain.errors import OutsideProject, RootMissing, Unreadable
from xarch.modules.rules.domain.rule import Rule
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
from xarch.modules.rules.domain.vocabulary import READING, SLOTS, Kind


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService, app: AppCheckService,
                 explaining: ExplainingService):
        self._service, self._locator, self._app, self._explaining = service, locator, app, explaining

    def explain_words(self, cmd: ExplainWords) -> WordsResult:
        """How a check is written, a category of its words or one word, from the vocabulary the engine reads; an
        address of no word comes back with the nearest ones."""
        typed = cmd.address.strip().strip(".")
        if typed == CHECKS:
            categories = tuple(_category(name) for name in explained.CATEGORIES)
            found = self._explaining.first_of(EXAMPLE_KEY, cmd.examples_from)
            location, rule = found if found is not None else ("", None)
            return ChecksShown(READING, tuple(SlotShown(s.name, s.meaning, s.accepts) for s in SLOTS), categories,
                               rule.key if rule is not None else "", location,
                               written((rule,), (rule.id,)) if rule is not None else "")
        if explained.category_at(typed):
            return WordsShown(_category(typed))
        at = explained.word_at(typed)
        if at is None:
            return UnknownWords(typed, explained.nearest(typed))
        category, word = at
        found = self._explaining.example(category, word.name, cmd.examples_from)
        location, rule = found if found is not None else ("", None)
        kind = word if isinstance(word, Kind) else None
        return WordShown(typed, category, word.name, word.meaning, getattr(word, "about", ""), explained.applies(word),
                         getattr(word, "side", ""), getattr(word, "value", "") or getattr(word, "values", ""),
                         tuple(FieldShown(*f) for f in explained.fields(kind)) if kind else (),
                         explained.needs(kind) if kind else (), kind.verb if kind else "",
                         rule.key or rule.id if rule is not None else "", location,
                         written((rule,), (rule.id,)) if rule is not None else "")

    def explain_rule(self, cmd: ExplainRule) -> RuleResult:
        """The rules a key of a profile expands to, written as checks; a key that expands to none comes back with
        why."""
        try:
            rules = self._explaining.rules_of(cmd.address, cmd.profile)
        except DomainError as e:
            return NoRuleShown(cmd.address, cmd.profile, e.reason)
        if not rules:
            return NoRuleShown(cmd.address, cmd.profile, "it expands to no rule of the engine here: the profile does not "
                                                         "set it, or it is checked by a check of its own")
        return RuleShown(cmd.address, cmd.profile, written(rules, _ids(rules)), len(rules))

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


CHECKS = "checks"
"""The address of how a check is written."""
EXAMPLE_KEY = "parts.names"
"""The key whose rule is the example of how a check is written: a short one, as most profiles set it."""


def _ids(rules: list[Rule]) -> list[str]:
    """An id for each rule written as a check: its own, then the part its scope names, then a number when two would
    be the same."""
    ids: list[str] = []
    for rule in rules:
        base = f"{rule.id}-{rule.scope.named_part}" if rule.scope.named_part else rule.id
        name, count = base, 1
        while name in ids:
            count += 1
            name = f"{base}-{count}"
        ids.append(name)
    return ids


def _category(name: str) -> CategoryShown:
    return CategoryShown(name, explained.MEANINGS[name],
                         tuple(WordLine(word.name, word.meaning) for word in explained.CATEGORIES[name]))


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
