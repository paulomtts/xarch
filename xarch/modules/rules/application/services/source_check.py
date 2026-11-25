from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic import (
    cycles,
    duplicates,
    enforcement,
    expansion,
    governed,
    known,
    scenarios,
    shared,
    stand_ins,
    twins,
)
from xarch.modules.rules.application.logic.engine import read, run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import (
    ApproximateView,
    EnforcementView,
    ExcludedView,
    FindingView,
    OwnCheckView,
)
from xarch.modules.rules.domain.errors import RootMissing
from xarch.modules.rules.domain.outcomes import Checked, Enforcement
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak


class SourceCheckService:
    """Every check of what the source says: the app's imports, its outside packages, the tests' imports by tier and
    the guards the profile switches on."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def view(self, state: Enforcement) -> EnforcementView:
        """The state of the check's enforcement as the enforcement section shows it."""
        return EnforcementView(
            state.ungoverned, tuple(enforcement.folders(state.ungoverned)),
            state.init_files, state.skipped, state.dynamic,
            state.weak, tuple(FindingView(f.key, enforcement.detail(f.item)) for f in state.strict),
            tuple(ExcludedView(enforcement.excluded_folder(state.app, e), e.reason) for e in state.excluded),
            state.language, tuple(ApproximateView(a.address, a.fact, a.note or "",
                                                  enforcement.approximation(a.address, a.fact, a.note or ""))
                                  for a in state.approximate),
            tuple(OwnCheckView(name, read, enforcement.reading(name, read)) for name, read in state.checks),
            state.known, state.translated)

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> Checked:
        """The violations below root and below tests, each given in full with its links followed, and the state of the
        check's enforcement; raises RootMissing when either is not a folder.

        Only the app's files that the profile governs are read: a file in a folder that is neither a part nor a
        folder of the layout (such as reference code kept as data) is never read, and is listed as ungoverned; a file
        below a folder the profile excludes is not looked at at all, and the folder is named in the enforcement. Every
        file below tests is read. The init files are looked for in the folder holding root, where `init` writes them.
        """
        absent = self._tree.absent(folder for folder in (root, tests) if folder is not None)
        if absent:
            raise RootMissing(absent[0])
        rules = resolved(self._profiles.profile(profile))
        extension = rules.language.extension
        paths = [p for p in self._tree.paths(root, extension) if not governed.excluded(rules, p)]
        marks = rules.language.immutable
        app = self._tree.read(root, [p for p in paths if governed.governed(rules, p)], immutable=marks)
        table = rules.scenarios.table if rules.scenarios is not None else \
            rules.framework.table if rules.framework is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests, extension), table, marks) \
            if tests is not None else []
        tests_root = tests.name if tests is not None else None
        shown = root.name
        unread = governed.unread(paths, rules, shown)
        book = expansion.book(rules)
        own = tuple(check.rule for check in rules.checks)
        facts = facts_of(app, test_files, rules, package, tests_root or "",
                         [*(r for group in book.values() for r in group), *own], unread)
        app = [f for f in app if f.error is None]
        test_files = [f for f in test_files if f.error is None]
        found = run(book["syntax"], facts, rules) + run(book["may-import"], facts, rules) + run(book["libraries"], facts,
                                                                                           rules)
        found += run(book["never-use"], facts, rules)
        found += cycles.violations(app, rules, package)
        found += run(book["tiers"], facts, rules)
        found += run(book["types-only tiers"], facts, rules)
        found += run(book["package-only"], facts, rules)
        covered = scenarios.violations(app, test_files, rules)
        found += covered + scenarios.plain(test_files, rules, covered)
        found += stand_ins.violations(app, test_files, rules, package, tests_root)
        found += run(book["must-import"], facts, rules)
        found += run(book["must-import tiers"], facts, rules)
        found += run(book["types-only parts"], facts, rules)
        found += run(book["no-callbacks"], facts, rules)
        found += run(book["names"], facts, rules)
        found += run(book["built-by"], facts, rules)
        found += run(book["private-imports"], facts, rules)
        found += duplicates.violations(app, rules)
        twinned = twins.checked(app, rules, package)
        found += twinned.violations
        found += shared.violations(app, rules, package)
        found += run(book["dead-code"], facts, rules)
        found += run(book["no-comments"], facts, rules)
        found += run(book["closed-tree"], facts, rules)
        written = run(own, facts, rules)
        found += [item for item in written if isinstance(item, Violation)]
        only = known.accepting(run(book["tests-only"], facts, rules), facts, rules)
        state = self._enforcement(root, package, profile, rules, app, test_files,
                                  governed.ungoverned(paths, rules, shown), tests_root,
                                  [*run(book["holds"], facts, rules), *run(book["immutable"], facts, rules)],
                                  run(book["untested"], facts, rules),
                                  [*run(book["pass-through"], facts, rules), *only.listed, *written])
        state = replace(state, checks=tuple((rule.id, read(rule, facts, rules)) for rule in own), known=only.known,
                        translated=twinned.translated)
        return Checked(tuple(found), replace(state, strict=enforcement.strict_findings(state)), rules)

    def _enforcement(self, resolved: Path, package: str, location: str, rules: Profile, app: list[SourceFile],
                     tests: list[SourceFile], ungoverned: list[str], tests_root: str | None,
                     listed: list[Violation | Weak], untested: list[Violation | Weak],
                     forwarding: list[Violation | Weak]) -> Enforcement:
        project = resolved.parent
        standing = self._profiles.standing(location, package)
        texts = [self._tree.text(project.joinpath(*file.path)) for file in standing.init_files]
        weak = enforcement.weak_of([*stand_ins.weak(app, tests, rules), *scenarios.weak(app, tests, rules), *forwarding,
                                    *listed], untested, tests_root is not None)
        return Enforcement(standing.guards_off, standing.baseline_off, tuple(ungoverned),
                           tuple(enforcement.drift(standing.init_files, texts)),
                           skipped=tuple(enforcement.skipped(tests, rules)),
                           dynamic=tuple(enforcement.dynamic([*app, *tests], rules)), weak=tuple(weak),
                           excluded=rules.excluded, app=resolved.name, language=rules.language.title,
                           approximate=rules.approximate, unplaced=enforcement.unplaced(standing.looser))
