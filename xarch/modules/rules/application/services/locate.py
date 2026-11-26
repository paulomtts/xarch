from __future__ import annotations

from dataclasses import replace

from xarch.kernel.placement import Place
from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.application.logic.where import accepted_in, applying, candidates, describe, resolve
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import (
    AcceptedImportView,
    CounterpartView,
    CoveringTest,
    Fake,
    InPart,
    InStructure,
    InTests,
    Locate,
    Located,
    NearestView,
    PartShown,
    ReachView,
    Support,
    TierInfoView,
    Ungoverned,
    Untested,
    WhereAnswer,
)
from xarch.modules.rules.domain.errors import OutsideProject
from xarch.modules.rules.domain.places import FakePlace, PartAt, PartPlace, Placed, StructurePlace, SuitePlace, UngovernedPlace
from xarch.modules.rules.domain.profile import PartInfo, Profile
from xarch.profile_values.tiers import CheckedTier


class LocateService:
    """Says what a path is, and what code there may do, before any is written."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def locate(self, cmd: Locate) -> Located:
        """What the path is, placed or not; raises OutsideProject for a path outside the project."""
        app = self._tree.resolved(cmd.cwd, cmd.app)
        tests = self._tree.resolved(cmd.cwd, cmd.tests) if cmd.tests is not None else None
        existing = self._tree.existing(candidates(cmd.path, cmd.cwd, app))
        found = resolve(cmd.path, cmd.cwd, app, tests, existing)
        if found is None:
            raise OutsideProject(cmd.path, app.parent)
        profile = resolved(self._profiles.profile(cmd.profile))
        placed = describe(profile, found, app, tests)
        return Located(_extras(_where(placed), placed, profile))


def _extras(answer: WhereAnswer, placed: Placed, profile: Profile) -> WhereAnswer:
    """The answer with the counterparts that apply to its path and, for a file of a part, the imports its part
    accepts there."""
    pairs = tuple(CounterpartView(paired.id, "/".join(paired.wants) + ("/" if paired.wants_folder else ""),
                                  "/".join(paired.at) + ("/" if paired.at_folder else ""), needs)
                  for paired, needs in applying(profile, placed.found))
    answer = replace(answer, counterparts=pairs)
    if isinstance(answer, InPart) and isinstance(placed, PartPlace) and placed.place.part is not None:
        answer = replace(answer, accepted=tuple(AcceptedImportView(entry.written, entry.why) for entry in
                                                accepted_in(profile, placed.place.part, placed.found.steps)))
    return answer


def _where(found: Placed) -> WhereAnswer:
    match found:
        case PartPlace():
            return InPart(found.found.shown, found.found.exists, _part(found.place, found.info, found.singular),
                          _reaches(found.reaches), found.may_import_text, found.libraries, found.uses_never,
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
                        found.may_import_text, tier.imports_types_only if tier is not None else (), found.uses_never,
                        _tier(tier) if tier is not None else None, found.may_use_fakes, found.fakes_path,
                        found.test_code_from, found.note, found.shared)
        case FakePlace():
            return Fake(found.found.shown, found.found.exists, found.fakes_path, found.test_code_from, found.note)


def _part(place: Place, info: PartInfo, singular: str) -> PartShown:
    return PartShown(place.part or "", info.shown, place.instance or "", singular, info.role, info.litmus,
                     info.litmus_list, info.optional)


def _reaches(reaches: tuple[PartAt, ...]) -> tuple[ReachView, ...]:
    return tuple(ReachView(r.target.part, r.target.scope, r.folder, r.path) for r in reaches)


def _nearest(nearest: tuple[PartAt, ...]) -> tuple[NearestView, ...]:
    return tuple(NearestView(n.target.part, n.folder, n.path) for n in nearest)


def _tier(tier: CheckedTier) -> TierInfoView:
    return TierInfoView(tier.name, tier.proves, tier.may_touch, tier.litmus, tier.litmus_list)


def _tested(found: PartPlace) -> CoveringTest | Untested | None:
    if found.tier is not None:
        return CoveringTest(_tier(found.tier), found.test_folder, found.test_file, found.test_folder + found.test_file)
    return Untested(found.untested) if found.untested else None
