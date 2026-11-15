"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.kernel.logic.origin import Origin
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.values import InitFile, PartInfo, Profile, Standing
from xarch.modules.spec.contract import FilesResult, OriginResult, ProfileRefused, ProfileView, ProjectFiles


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def profile(self, location: str) -> ProfileView: ...

    def origin(self, location: str) -> OriginResult: ...

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult: ...


class SpecProfiles:
    """Satisfies rules' Profiles port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def profile(self, location: str) -> Profile:
        view = self._spec.profile(location)
        parts, guards = view.parts, view.guards
        return Profile(parts={p.name: p.pattern for p in parts}, rules={p.name: p.may_import for p in parts},
                       folders=view.folders,
                       tiers=view.tiers,
                       libraries=None if view.libraries is None else dict(view.libraries),
                       fakes=view.fakes,
                       repeats=view.repeats, package_only=guards.package_only,
                       scenarios=guards.scenarios, no_comments=guards.no_comments, stand_ins=guards.stand_ins,
                       closed_tree=guards.closed_tree,
                       must_import={p.name: p.must_import for p in parts if p.must_import},
                       no_duplicates=guards.no_duplicates, no_twins=guards.no_twins, dead_code=guards.dead_code, untested=guards.untested,
                       pass_through=guards.pass_through, holds={p.name: p.holds for p in parts if p.holds},
                       types_only={p.name: p.types_only for p in parts if p.types_only},
                       no_callbacks=tuple(p.name for p in parts if p.no_callbacks),
                       names={p.name: p.names for p in parts if p.names},
                       built_by={p.name: p.built_by for p in parts if p.built_by},
                       private_imports=guards.private_imports,
                       framework=view.framework,
                       forbidden={p.name: p.forbidden for p in parts if p.forbidden},
                       info={p.name: PartInfo(p.role, p.litmus, p.shown, p.untested) for p in parts},
                       excluded=view.excluded, hints=dict(view.hints), language=view.language,
                       reserved=dict(view.reserved), approximate=view.approximate)

    def standing(self, location: str, app: str) -> Standing:
        """No init files when the profile cannot write them for this app, which `init` reports when it refuses; a
        profile whose origin cannot be worked out raises ProfileUnusable."""
        match self._spec.origin(location):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case Origin() as origin:
                pass
        match self._spec.files(location, app, presets=False):
            case ProjectFiles(files):
                found = tuple(InitFile(file.path, _text(file.content), file.pinned) for file in files)
            case ProfileRefused():
                found = ()
        return Standing(origin, found)


def _text(content: str | bytes) -> str:
    """What `check` compares a pinned file with: a file copied as bytes is compared as the text it holds."""
    return content if isinstance(content, str) else content.decode("utf-8", errors="replace")
