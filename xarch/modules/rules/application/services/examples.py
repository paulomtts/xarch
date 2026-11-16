from __future__ import annotations

from dataclasses import replace

from xarch.kernel.logic.examples import is_test_example
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.own_checks import held_problems, made
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import OwnCheck
from xarch.modules.rules.domain.values import Profile, SourceFile
from xarch.profile_values.checks import ChecksHeld


class ExamplesService:
    """The checks a profile writes itself, held to their examples: each must find something in the code it is flagged
    by, and nothing in its clean code, each a small project of files read as the app's (or, below tests/, as the
    tests'), the app being the package app names. A check that cannot be made has its problems instead, and the
    others are held all the same."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def held(self, location: str, app: str) -> ChecksHeld:
        """What is wrong with the profile's own checks, in the profile's order, each problem at its address: why a
        check cannot be made, or how one made does not hold to its examples; and how many checks the profile writes
        itself, made or not. Raises DomainError when the profile cannot be read."""
        profile = self._profiles.profile(location)
        found: list[str] = []
        for name, written in profile.written.items():
            checks = made({name: written}, profile)
            found += checks.problems
            for own in checks.checks:
                found += held_problems(own.rule.id, self._found(own, own.flagged, profile, app),
                                       self._found(own, own.clean, profile, app))
        return ChecksHeld(tuple(found), len(profile.written))

    def _found(self, own: OwnCheck, files: tuple[tuple[str, str], ...], profile: Profile,
               app: str) -> list[Violation | Weak]:
        tests = profile.default_tests
        read = [(tuple(path.split("/")), self._tree.parsed(code)) for path, code in files]
        app_files = [self._placed(parsed, (app, *steps), steps) for steps, parsed in read
                     if not is_test_example(steps, tests)]
        test_files = [self._placed(parsed, steps, steps[1:]) for steps, parsed in read if is_test_example(steps, tests)]
        rules = (own.rule,)
        return run(rules, facts_of(app_files, test_files, profile, app, tests, rules), profile)

    def _placed(self, parsed: SourceFile, shown: tuple[str, ...], path: tuple[str, ...]) -> SourceFile:
        return replace(parsed, name="/".join(shown), path=path)
