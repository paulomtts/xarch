"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.errors import NoProfile, ProfileUnusable, Unloaded
from xarch.modules.rules.domain.outcomes import InitFile, Known, Standing
from xarch.modules.rules.domain.profile import Asked, PartInfo, Profile
from xarch.modules.rules.domain.published import KeyFacts, Loosened, Resemblance, Reviewed
from xarch.modules.spec.contract import (
    DEFAULT_TESTS,
    CheckProfile,
    CheckResult,
    Explain,
    ExplainResult,
    FilesResult,
    KeyExplained,
    KnownProfiles,
    KnownResult,
    NoProfileChosen,
    Origin,
    OriginResult,
    ProfileChecked,
    ProfileRefused,
    ProfileResult,
    ProfileView,
    ProjectFiles,
)


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def profile(self, location: str) -> ProfileResult: ...

    def origin(self, location: str) -> OriginResult: ...

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult: ...

    def known(self, app: Path) -> KnownResult: ...

    def explain(self, cmd: Explain) -> ExplainResult: ...

    def check_profile(self, cmd: CheckProfile) -> CheckResult: ...


class SpecProfiles:
    """Satisfies rules' Profiles port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def profile(self, location: str) -> Profile:
        """The profile, with the checks it writes itself as spec read them; one spec refuses raises ProfileUnusable."""
        match self._spec.profile(location):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case ProfileView() as view:
                pass
        parts, guards = view.parts, view.guards
        return Profile(parts={p.name: p.pattern for p in parts}, rules={p.name: p.imports_may for p in parts},
                       folders=view.folders,
                       tiers=view.tiers,
                       imports_libraries=None if view.imports_libraries is None else dict(view.imports_libraries),
                       fakes=view.fakes,
                       repeats=view.repeats, package_only=guards.package_only,
                       scenarios=guards.scenarios, no_comments=guards.no_comments, stand_ins=guards.stand_ins,
                       closed_tree=guards.closed_tree,
                       imports_must={p.name: p.imports_must for p in parts if p.imports_must},
                       no_duplicates=guards.no_duplicates, no_twins=guards.no_twins,
                       no_twins_renamed=guards.no_twins_renamed, no_twins_subset=guards.no_twins_subset,
                       no_twins_translated=guards.no_twins_translated,
                       dead_code=guards.dead_code, untested=guards.untested, tests_only=guards.tests_only,
                       tests_only_known=guards.tests_only_known,
                       pass_through=guards.pass_through,
                       holds={p.name: tuple(h.kind for h in p.holds) for p in parts if p.holds},
                       holds_immutable={p.name: tuple(h.kind for h in p.holds if h.immutable) for p in parts
                                        if any(h.immutable for h in p.holds)},
                       imports_types_only={p.name: p.imports_types_only for p in parts if p.imports_types_only},
                       no_callbacks=guards.no_callbacks,
                       holds_names={p.name: {h.kind: h.names for h in p.holds if h.names} for p in parts
                                    if any(h.names for h in p.holds)},
                       holds_built_by={p.name: h.built_by for p in parts for h in p.holds if h.built_by},
                       shared={p.name: p.shared for p in parts if p.shared is not None},
                       imports_accepted={p.name: p.imports_accepted for p in parts if p.imports_accepted},
                       private_imports=guards.private_imports,
                       framework=view.framework,
                       uses_never={p.name: p.uses_never for p in parts if p.uses_never},
                       info={p.name: PartInfo(p.role, p.litmus, p.shown, p.untested) for p in parts},
                       excluded=view.excluded, hints=dict(view.hints), language=view.language,
                       reserved=dict(view.reserved),
                       approximate=view.approximate, written=dict(view.checks), default_tests=DEFAULT_TESTS,
                       asked={name: Asked(asked.reads, asked.within, asked.keep, asked.flagged_examples,
                                          asked.clean_examples) for name, asked in view.evals.items()})

    def known(self, app: Path) -> Known:
        """None configured is no profile in force; one spec refuses raises ProfileUnusable with its reason."""
        match self._spec.known(app):
            case KnownProfiles(in_force, bundled):
                return Known(in_force, bundled)
            case NoProfileChosen(known):
                return Known(None, known)
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)

    def key(self, address: str) -> KeyFacts:
        """An explanation spec refuses raises ProfileUnusable with its reason."""
        match self._spec.explain(Explain(address)):
            case KeyExplained() as explained:
                return KeyFacts(explained.example, explained.name, explained.holder, explained.read_by)
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
        return KeyFacts()

    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        """What spec's check of the profile found, compared with the profile against names when it is given, in rules'
        terms: a profile that does not load raises Unloaded with the loader's problems, none chosen NoProfile with the
        profiles known, and one spec refuses ProfileUnusable."""
        match self._spec.check_profile(CheckProfile(app, target, against)):
            case ProfileChecked(location, problems, _, None):
                raise Unloaded(location, tuple(problem.text for problem in problems))
            case ProfileChecked(location, problems, files, Origin() as origin):
                looser = tuple(Loosened(item.key, item.part, item.what, item.sentence) for item in origin.looser)
                return Reviewed(location, tuple(problem.text for problem in problems), files,
                                Resemblance(origin.bundled, origin.compared, looser, origin.chosen_by, origin.match,
                                            origin.low, origin.counts, origin.only_here, origin.only_there,
                                            origin.elsewhere, origin.higher, origin.based_on, origin.anchor))
            case NoProfileChosen(known):
                raise NoProfile(known)
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)

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
        return Standing(origin.guards_off, origin.baseline_off, found,
                        tuple(Loosened(item.key, item.part, item.what, item.sentence) for item in origin.looser))


def _text(content: str | bytes) -> str:
    """What `check` compares a pinned file with: a file copied as bytes is compared as the text it holds."""
    return content if isinstance(content, str) else content.decode("utf-8", errors="replace")
