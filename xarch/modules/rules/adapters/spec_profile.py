"""Profiles filled by the spec module: the only file in rules that names spec, and it names only spec's contract."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from xarch.kernel.capabilities import FACTS, Shortfall
from xarch.kernel.logic.capabilities import shortfalls
from xarch.modules.rules.domain.errors import ChecksRefused, ProfileUnusable, RuleRefused
from xarch.modules.rules.domain.rule import (
    EXISTING,
    MAY_NOT,
    MAY_ONLY,
    MUST_BE_REACHED,
    MUST_REACH,
    Condition,
    Match,
    OwnCheck,
    Rule,
    Saying,
    Scope,
)
from xarch.modules.rules.domain.values import InitFile, PartInfo, Profile, Standing
from xarch.modules.rules.domain.vocabulary import NAMES, PLACES, TARGETS
from xarch.modules.spec.contract import (
    DEFAULT_TESTS,
    FilesResult,
    Origin,
    OriginResult,
    ProfileRefused,
    ProfileResult,
    ProfileView,
    ProjectFiles,
)
from xarch.profile_values.language import CheckedLanguage


class _Spec(Protocol):
    """The little rules uses of spec's controller."""

    def profile(self, location: str) -> ProfileResult: ...

    def origin(self, location: str) -> OriginResult: ...

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult: ...


class SpecProfiles:
    """Satisfies rules' Profiles port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def profile(self, location: str) -> Profile:
        """The profile, its own checks made into rules; one spec refuses raises ProfileUnusable, and one whose checks
        cannot be made ChecksRefused."""
        match self._spec.profile(location):
            case ProfileRefused(reason):
                raise ProfileUnusable(reason)
            case ProfileView() as view:
                pass
        parts, guards = view.parts, view.guards
        written = WrittenChecks()
        checks = written.own(view.checks, view.language)
        return Profile(parts={p.name: p.pattern for p in parts}, rules={p.name: p.may_import for p in parts},
                       folders=view.folders,
                       tiers=view.tiers,
                       libraries=None if view.libraries is None else dict(view.libraries),
                       fakes=view.fakes,
                       repeats=view.repeats, package_only=guards.package_only,
                       scenarios=guards.scenarios, no_comments=guards.no_comments, stand_ins=guards.stand_ins,
                       closed_tree=guards.closed_tree,
                       must_import={p.name: p.must_import for p in parts if p.must_import},
                       no_duplicates=guards.no_duplicates, no_twins=guards.no_twins,
                       no_twins_renamed=guards.no_twins_renamed, no_twins_subset=guards.no_twins_subset,
                       dead_code=guards.dead_code, untested=guards.untested,
                       pass_through=guards.pass_through, holds={p.name: p.holds for p in parts if p.holds},
                       types_only={p.name: p.types_only for p in parts if p.types_only},
                       no_callbacks=tuple(p.name for p in parts if p.no_callbacks),
                       names={p.name: p.names for p in parts if p.names},
                       built_by={p.name: p.built_by for p in parts if p.built_by},
                       shared={p.name: p.shared for p in parts if p.shared is not None},
                       private_imports=guards.private_imports,
                       framework=view.framework,
                       forbidden={p.name: p.forbidden for p in parts if p.forbidden},
                       info={p.name: PartInfo(p.role, p.litmus, p.shown, p.untested) for p in parts},
                       excluded=view.excluded, hints=dict(view.hints), language=view.language,
                       reserved=dict(view.reserved),
                       approximate=(*view.approximate, *written.approximate(checks, view.language)), checks=checks,
                       tests_folder=DEFAULT_TESTS)

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
        return Standing(origin.guards_off, origin.baseline_off, found)


def _text(content: str | bytes) -> str:
    """What `check` compares a pinned file with: a file copied as bytes is compared as the text it holds."""
    return content if isinstance(content, str) else content.decode("utf-8", errors="replace")


class WrittenChecks:
    """The checks a profile writes itself, as spec reads their syntax (see spec's written_checks), made into rules: a
    check that names a word the vocabulary does not hold, or one that does not apply, or that needs a fact the
    language's reader does not supply, is refused with every problem of every check at once (ChecksRefused)."""

    def own(self, checks: Mapping[str, Mapping[str, Any]], language: CheckedLanguage) -> tuple[OwnCheck, ...]:
        found: list[OwnCheck] = []
        problems: list[str] = []
        for name, body in checks.items():
            try:
                rule = self._rule(name, body)
            except RuleRefused as refused:
                problems += [f"checks.{name}.{problem}" for problem in refused.problems]
                continue
            problems += self._supplied(name, rule, language)
            found.append(OwnCheck(rule, body["examples"]["flagged"], body["examples"]["clean"]))
        if problems:
            raise ChecksRefused(tuple(problems))
        return tuple(found)

    def approximate(self, checks: tuple[OwnCheck, ...], language: CheckedLanguage) -> tuple[Shortfall, ...]:
        """The checks that read a fact the language's reader supplies only partly, by the fact."""
        supplies = {s.fact: s for s in language.supplies or ()}
        return tuple(short for check in checks for short in shortfalls(check.rule.key, check.rule.needs, supplies)
                     if short.note is not None)

    def _supplied(self, name: str, rule: Rule, language: CheckedLanguage) -> list[str]:
        if language.supplies is None:
            return []
        supplies = {s.fact: s for s in language.supplies}
        return [f"checks.{name}: needs {short.fact} ({FACTS[short.fact]}), which the reader of {language.title} does "
                "not supply: read another kind of fact, or drop the check"
                for short in shortfalls(rule.key, rule.needs, supplies) if short.note is None]

    def _rule(self, name: str, body: Mapping[str, Any]) -> Rule:
        quantifier = next(slot for slot in (MAY_NOT, MAY_ONLY, MUST_REACH, MUST_BE_REACHED) if slot in body)
        reach = body[quantifier] if quantifier in (MUST_REACH, MUST_BE_REACHED) else {}
        targets = (EXISTING if quantifier == MUST_BE_REACHED else
                   tuple(self._match(t) for t in (reach["targets"] if quantifier == MUST_REACH else body[quantifier])))
        sayings = (*(Saying(case["message"], case["fix"], self._conditions(case["when"]), case["once_per"])
                     for case in body["cases"]),
                   Saying(body["message"], body["fix"], (), body["once_per"]))
        return Rule(name, self._scope(body["in"]), body["read"], quantifier, targets, sayings,
                    keep=self._conditions(body["keep"]), exempt=self._conditions(body["except"]), mode=body["mode"],
                    key=f"checks.{name}", links=reach.get("through", ()),
                    via=self._conditions(reach.get("through_only", ())),
                    roots=self._scope(reach["from"]) if "from" in reach else None, spread=reach.get("then_through", ()),
                    elsewhere=reach.get("by_another_file", False))

    def _scope(self, scope: Mapping[str, Any]) -> Scope:
        return Scope(scope["files"], scope["part"], scope["tier"], self._conditions(scope["where"]))

    def _conditions(self, texts: tuple[str, ...]) -> tuple[Condition, ...]:
        return tuple(Condition.of(text) for text in texts)

    def _match(self, target: Mapping[str, Any]) -> Match:
        kind, values = target["kind"], target["values"]
        written = next((k.values for k in TARGETS if k.name == kind), "")
        if written == PLACES:
            return Match(kind, places=values)
        if written == NAMES:
            return Match(kind, names=tuple(("", value[1:]) if value.startswith(".") else tuple(value.split("."))
                                           for value in values))
        return Match(kind, words=tuple(values))
