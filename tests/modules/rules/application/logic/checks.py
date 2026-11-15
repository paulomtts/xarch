"""The checks the rules as data now are, called as each check's unit tests always called it: the rules a profile's keys
expand to, run by the engine over the facts of the files given."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic import expansion
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.values import Profile, SourceFile


def libraries(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.libraries(profile), facts_of(files, [], profile, root), profile)


def forbidden(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return run(expansion.forbidden(profile), facts_of(app, tests, profile, ""), profile)


def package_only(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
                 root: str) -> list[Violation | Weak]:
    return run(expansion.package_only(profile), facts_of(app, tests, profile, root), profile)


def private_imports(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
                    tests_root: str) -> list[Violation | Weak]:
    return run(expansion.private_imports(profile), facts_of(app, tests, profile, root, tests_root), profile)


def built_by(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.built_by(profile), facts_of(app, [], profile, root), profile)


def rules(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.rules(profile), facts_of(files, [], profile, root), profile)
