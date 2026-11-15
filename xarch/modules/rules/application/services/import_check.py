from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic import (
    closed_tree,
    comments,
    cycles,
    enforcement,
    forbidden,
    libraries,
    package_only,
    scenarios,
    stand_ins,
    tier_imports,
    types_only,
)
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import RootMissing
from xarch.modules.rules.domain.imports import dotted, violations
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Enforcement, Excluded, Profile, SourceFile

SYNTAX = "syntax"
"""The rule of a file that does not parse."""


class ImportCheck:
    """Every check of what the source says: the app's imports, its outside packages, the tests' imports by tier and
    the guards the profile switches on."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def check(self, root: Path, package: str, profile: str,
              tests: Path | None = None) -> tuple[list[Violation], Enforcement]:
        """The violations below root and below tests, and the state of the check's enforcement; raises RootMissing
        when either is not a folder.

        Only the app's files that the profile governs are read: a file in a folder that is neither a part nor a
        folder of the layout (such as reference code kept as data) is never read, and is listed as ungoverned; a file
        below a folder the profile excludes is not looked at at all, and the folder is named in the enforcement. Every
        file below tests is read. The init files are looked for in the folder holding root, where `init` writes them.
        """
        for folder in (root, tests):
            if folder is not None and not self._tree.is_dir(folder):
                raise RootMissing(folder)
        rules = self._profiles.profile(profile)
        paths = [p for p in self._tree.paths(root) if not _excluded(rules, p)]
        app = self._tree.read(root, [p for p in paths if _governed(rules, p)])
        table = rules.scenarios.table if rules.scenarios is not None else None
        test_files = self._tree.read(tests, self._tree.paths(tests), table) if tests is not None else []
        broken = [Violation(f.name, f.error[0], f.error[1], SYNTAX, "correct the syntax so that the file can be read")
                  for f in (*app, *test_files) if f.error is not None]
        app = [f for f in app if f.error is None]
        test_files = [f for f in test_files if f.error is None]
        tests_root = tests.absolute().resolve().name if tests is not None else ""
        found = broken + violations(app, rules, package) + libraries.violations(app, rules, package)
        found += forbidden.violations(app, test_files, rules)
        found += cycles.violations(app, rules, package)
        found += tier_imports.violations(test_files, app, rules, package, tests_root)
        found += types_only.violations(test_files, app, rules, package)
        found += package_only.violations(app, test_files, rules, package)
        found += scenarios.violations(app, test_files, rules)
        found += stand_ins.violations(app, test_files, rules, package, tests is not None)
        if rules.no_comments:
            found += comments.violations([*app, *test_files])
        shown = root.absolute().resolve().name
        found += closed_tree.violations(paths, rules, shown)
        state = self._enforcement(root, package, profile, rules, app, test_files,
                                  closed_tree.ungoverned(paths, rules, shown))
        return found, replace(state, strict=enforcement.strict_findings(state))

    def _enforcement(self, root: Path, package: str, location: str, rules: Profile, app: list[SourceFile],
                     tests: list[SourceFile], ungoverned: list[str]) -> Enforcement:
        project = root.absolute().resolve().parent
        files = self._profiles.init_files(location, package)
        texts = [self._tree.text(project.joinpath(*file.path)) for file in files]
        weak = stand_ins.weak(app, tests, rules) + scenarios.weak(app, tests, rules)
        shown = [Excluded("/".join((root.absolute().resolve().name, *e.path)), e.reason) for e in rules.excluded]
        return Enforcement(self._profiles.origin(location), tuple(ungoverned), tuple(enforcement.drift(files, texts)),
                           skipped=tuple(enforcement.skipped(tests, rules)),
                           dynamic=tuple(enforcement.dynamic([*app, *tests])), weak=tuple(weak),
                           excluded=tuple(shown))


def _excluded(profile: Profile, path: tuple[str, ...]) -> bool:
    return any(path[:len(e.path)] == e.path for e in profile.excluded)


def _governed(profile: Profile, path: tuple[str, ...]) -> bool:
    return place(profile, dotted(path)[0]) is not None

