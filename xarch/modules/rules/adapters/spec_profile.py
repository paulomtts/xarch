"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.kernel.errors import DomainError
from xarch.modules.rules.domain.values import (
    Exclusion,
    Fakes,
    Fixture,
    Framework,
    InitFile,
    Language,
    Loosened,
    Origin,
    PartInfo,
    Profile,
    Scenarios,
    TableForm,
    TestTier,
)
from xarch.modules.rules.domain.values import StandIns as StandInNames
from xarch.modules.spec.contract import GuardsView, ProfileOrigin, ProfileView, ProjectFile


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def profile(self, location: str) -> ProfileView: ...

    def origin(self, location: str) -> ProfileOrigin: ...

    def files(self, profile: str, app: str, presets: bool = True) -> tuple[ProjectFile, ...]: ...


class SpecProfiles:
    """Satisfies rules' Profiles port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def profile(self, location: str) -> Profile:
        view = self._spec.profile(location)
        parts, guards = view.parts, view.guards
        return Profile(parts={p.name: p.pattern for p in parts}, rules={p.name: p.may_import for p in parts},
                       folders=view.folders,
                       tiers=tuple(TestTier(t.name, t.subject, t.folder, t.types_only, t.forbidden, t.proves,
                                            t.may_touch, t.litmus, t.one_file_per, t.may_import, t.must_import)
                                   for t in view.tiers),
                       libraries=None if view.libraries is None else dict(view.libraries),
                       fakes=Fakes(view.fakes.folder, view.fakes.stand_in_for, view.fakes.prefix)
                       if view.fakes is not None else None,
                       repeats=view.repeats, package_only=guards.package_only,
                       scenarios=_scenarios(guards), no_comments=guards.no_comments, stand_ins=_stand_ins(guards),
                       closed_tree=guards.closed_tree,
                       must_import={p.name: p.must_import for p in parts if p.must_import},
                       no_duplicates=guards.no_duplicates, dead_code=guards.dead_code, untested=guards.untested,
                       pass_through=guards.pass_through, holds={p.name: p.holds for p in parts if p.holds},
                       types_only={p.name: p.types_only for p in parts if p.types_only},
                       no_callbacks=tuple(p.name for p in parts if p.no_callbacks),
                       names={p.name: p.names for p in parts if p.names},
                       built_by={p.name: p.built_by for p in parts if p.built_by},
                       private_imports=guards.private_imports,
                       framework=Framework(view.framework.files, view.framework.functions, view.framework.skips)
                       if view.framework is not None else None,
                       forbidden={p.name: p.forbidden for p in parts if p.forbidden},
                       info={p.name: PartInfo(p.role, p.litmus, p.shown, p.untested) for p in parts},
                       excluded=tuple(Exclusion(e.path, e.reason) for e in view.excluded), hints=dict(view.hints),
                       language=Language(view.language.title, view.language.extension, view.language.package_file,
                                         view.language.interface, view.language.dynamic))

    def origin(self, location: str) -> Origin:
        found = self._spec.origin(location)
        return Origin(found.location, found.bundled, found.closest, found.guards_off, found.baseline_off,
                      tuple(Loosened(item.key, item.part, item.what, item.sentence) for item in found.looser))

    def init_files(self, location: str, app: str) -> tuple[InitFile, ...]:
        """None when the profile cannot write them for this app, which `init` reports when it refuses."""
        try:
            files = self._spec.files(location, app, presets=False)
        except DomainError:
            return ()
        return tuple(InitFile(file.path, _text(file.content), file.pinned) for file in files)


def _scenarios(guards: GuardsView) -> Scenarios | None:
    found = guards.scenarios
    if found is None:
        return None
    table = found.table
    return Scenarios(found.results, found.tier, found.suffix, found.columns,
                     TableForm(table.decorator, table.row, table.id, table.keywords), found.file)


def _stand_ins(guards: GuardsView) -> StandInNames | None:
    found = guards.stand_ins
    if found is None:
        return None
    return StandInNames(found.mocks, found.autospec, found.spec,
                        tuple(Fixture(f.name, f.mocks, f.autospec) for f in found.fixtures))


def _text(content: str | bytes) -> str:
    """What `check` compares a pinned file with: a file copied as bytes is compared as the text it holds."""
    return content if isinstance(content, str) else content.decode("utf-8", errors="replace")
