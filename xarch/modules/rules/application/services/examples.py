from __future__ import annotations

from dataclasses import replace

from xarch.kernel.errors import DomainError
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import ChecksRefused
from xarch.modules.rules.domain.rule import OwnCheck
from xarch.modules.rules.domain.values import Profile, SourceFile

TESTS = "tests"
"""The folder an example's path starts with when its file is a test, and the root package of the tests."""


class ExamplesService:
    """The checks a profile writes itself, held to their examples: each must find something in the code it is flagged
    by, and nothing in its clean code, each a small project of files read as the app's (or, below tests/, as the
    tests'), the app being the package app names."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def problems(self, location: str, app: str) -> tuple[list[str], int]:
        """What is wrong with the profile's own checks, each problem at its address, and how many checks it has; a
        profile whose checks cannot be made has those problems."""
        try:
            profile = resolved(self._profiles.profile(location))
        except ChecksRefused as refused:
            return list(refused.problems), 0
        except DomainError as e:
            return [e.reason], 0
        found: list[str] = []
        for own in profile.checks:
            flagged, clean = self._found(own, own.flagged, profile, app), self._found(own, own.clean, profile, app)
            where = f"checks.{own.rule.id}.examples"
            if not flagged:
                found.append(f"{where}.flagged: the check finds nothing in it: make the code hold what the check is "
                             "written to find, or correct the check")
            if clean:
                first = clean[0]
                found.append(f"{where}.clean: the check finds {len(clean)} in it, the first "
                             f"{first.file}:{first.line}: {first.message}: make the code clean, or correct the check")
        return found, len(profile.checks)

    def _found(self, own: OwnCheck, files: tuple[tuple[str, str], ...], profile: Profile, app: str) -> list:
        read = [(path.split("/"), self._tree.parsed(code)) for path, code in files]
        app_files = [self._placed(parsed, (app, *steps), tuple(steps)) for steps, parsed in read if steps[0] != TESTS]
        test_files = [self._placed(parsed, tuple(steps), tuple(steps[1:])) for steps, parsed in read if steps[0] == TESTS]
        rules = (own.rule,)
        return run(rules, facts_of(app_files, test_files, profile, app, TESTS, rules), profile)

    def _placed(self, parsed: SourceFile, shown: tuple[str, ...], path: tuple[str, ...]) -> SourceFile:
        return replace(parsed, name="/".join(shown), path=path)
