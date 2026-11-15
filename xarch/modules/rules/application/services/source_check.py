from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.rules.application.logic import (
    closed_tree,
    cycles,
    dead_code,
    duplicates,
    enforcement,
    expansion,
    holds,
    must_import,
    pass_through,
    scenarios,
    stand_ins,
    twins,
)
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import RootMissing
from xarch.modules.rules.domain.values import Checked, Enforcement, Profile, SourceFile


class SourceCheckService:
    """Every check of what the source says: the app's imports, its outside packages, the tests' imports by tier and
    the guards the profile switches on."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> Checked:
        """The violations below root and below tests, and the state of the check's enforcement; raises RootMissing
        when either is not a folder.

        Only the app's files that the profile governs are read: a file in a folder that is neither a part nor a
        folder of the layout (such as reference code kept as data) is never read, and is listed as ungoverned; a file
        below a folder the profile excludes is not looked at at all, and the folder is named in the enforcement. Every
        file below tests is read. The init files are looked for in the folder holding root, where `init` writes them.
        """
        absent = self._tree.absent(folder for folder in (root, tests) if folder is not None)
        if absent:
            raise RootMissing(absent[0])
        rules = self._profiles.profile(profile)
        extension = rules.language.extension
        paths = [p for p in self._tree.paths(root, extension) if not closed_tree.excluded(rules, p)]
        app = self._tree.read(root, [p for p in paths if closed_tree.governed(rules, p)])
        table = rules.scenarios.table if rules.scenarios is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table) if tests is not None else []
        tests_root = self._tree.resolved(tests).name if tests is not None else ""
        resolved = self._tree.resolved(root)
        shown = resolved.name
        unread = [SourceFile("/".join((shown, *p)), p, ()) for p in paths if not closed_tree.governed(rules, p)]
        book = expansion.book(rules)
        facts = facts_of(app, test_files, rules, package, tests_root, [r for group in book.values() for r in group],
                         unread)
        app = [f for f in app if f.error is None]
        test_files = [f for f in test_files if f.error is None]
        found = run(book["syntax"], facts, rules) + run(book["rules"], facts, rules) + run(book["libraries"], facts,
                                                                                           rules)
        found += run(book["forbidden"], facts, rules)
        found += cycles.violations(app, rules, package)
        found += run(book["tiers"], facts, rules)
        found += run(book["types-only tiers"], facts, rules)
        found += run(book["package-only"], facts, rules)
        found += scenarios.violations(app, test_files, rules)
        found += stand_ins.violations(app, test_files, rules, package, tests_root if tests is not None else None)
        found += must_import.violations(app, rules, package)
        found += must_import.tier_violations(test_files, app, rules, package, tests_root)
        found += run(book["types-only parts"], facts, rules)
        found += run(book["no-callbacks"], facts, rules)
        found += run(book["names"], facts, rules)
        found += run(book["built-by"], facts, rules)
        found += run(book["private-imports"], facts, rules)
        found += duplicates.violations(app, rules)
        found += twins.violations(app, rules)
        found += dead_code.violations(app, test_files, rules, tests is not None)
        found += run(book["no-comments"], facts, rules)
        found += run(book["closed-tree"], facts, rules)
        state = self._enforcement(resolved, package, profile, rules, app, test_files,
                                  closed_tree.ungoverned(paths, rules, shown), tests_root if tests is not None else None)
        return Checked(tuple(found), replace(state, strict=enforcement.strict_findings(state)), rules)

    def _enforcement(self, resolved: Path, package: str, location: str, rules: Profile, app: list[SourceFile],
                     tests: list[SourceFile], ungoverned: list[str], tests_root: str | None) -> Enforcement:
        project = resolved.parent
        standing = self._profiles.standing(location, package)
        texts = [self._tree.text(project.joinpath(*file.path)) for file in standing.init_files]
        weak = stand_ins.weak(app, tests, rules) + scenarios.weak(app, tests, rules) + pass_through.weak(app, rules)
        weak += holds.weak(app, rules, package)
        if tests_root is not None:
            weak += dead_code.untested(app, tests, rules, package, tests_root)
        return Enforcement(standing.origin, tuple(ungoverned), tuple(enforcement.drift(standing.init_files, texts)),
                           skipped=tuple(enforcement.skipped(tests, rules)),
                           dynamic=tuple(enforcement.dynamic([*app, *tests], rules)), weak=tuple(weak),
                           excluded=rules.excluded, app=resolved.name, language=rules.language.title,
                           approximate=rules.approximate)
