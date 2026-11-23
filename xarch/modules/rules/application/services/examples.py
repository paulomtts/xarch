from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic import asked as evals
from xarch.modules.rules.application.logic.asked import project
from xarch.modules.rules.application.logic.engine import kept, run
from xarch.modules.rules.application.logic.own_checks import held_problems, made
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import ChecksHeld, ProfileHeld
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import OwnCheck


class ExamplesService:
    """A profile checked without an app: what spec's check of it finds, and the checks it writes itself held to their
    examples: each must find something in the code it is flagged by, and nothing in its clean code, each a small
    project of files read as the app's (or, below tests/, as the tests'), the app being the package the app folder
    names. A check that cannot be made has its problems instead, and the others are held all the same. The evals it
    writes itself are held to their examples statically: each must read something in every example file."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def check(self, app: Path, target: str | None) -> ProfileHeld:
        """The profile target names, else the one configured for the project holding the app folder, checked, its own
        checks held to their examples; raises Unloaded when it does not load, NoProfile when none is chosen, and
        DomainError when it cannot be used."""
        reviewed = self._profiles.reviewed(app, target)
        return ProfileHeld(reviewed, self._held(reviewed.location, app.name))

    def _held(self, location: str, app: str) -> ChecksHeld:
        """What is wrong with the profile's own checks, in the profile's order, each problem at its address: why a
        check cannot be made, or how one made does not hold to its examples; how many checks the profile writes
        itself, made or not; and the same of the evals it writes itself."""
        profile = self._profiles.profile(location)
        found: list[str] = []
        unread: list[str] = []
        for name, written in profile.written.items():
            checks = made({name: written}, profile)
            found += checks.problems
            for own in checks.checks:
                found += held_problems(own.rule.id, self._found(own, own.flagged, profile, app),
                                       self._found(own, own.clean, profile, app))
        for name, asked in profile.asked.items():
            rule, problems = evals.made(name, asked, profile.language)
            unread += problems
            for side, files in (("flagged", asked.flagged), ("clean", asked.clean)) if rule is not None else ():
                facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                          private=profile.language.private,
                                                          special=profile.language.special)) for path, code in files],
                                profile, app, (rule,))
                unread += evals.unread(name, side, files, kept(rule, facts, profile), asked.reads)
        return ChecksHeld(tuple(found), len(profile.written), tuple(unread), len(profile.asked))

    def _found(self, own: OwnCheck, files: tuple[tuple[str, str], ...], profile: Profile,
               app: str) -> list[Violation | Weak]:
        rules = (own.rule,)
        facts = project([(path, self._tree.parsed(code, profile.language.standard_modules,
                                                  private=profile.language.private,
                                                  special=profile.language.special)) for path, code in files],
                        profile, app, rules)
        return run(rules, facts, profile)
