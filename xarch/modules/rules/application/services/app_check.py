from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.application.logic.ordered import ordered
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.contract import AppChecked
from xarch.modules.rules.domain.errors import RootMissing


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, tree: SourceTree):
        self._source, self._structure, self._tree = source, structure, tree

    def check(self, root: Path, profile: str, tests: Path | None, cwd: Path, strict: bool) -> AppChecked:
        """The violations of the source and of the structure, in order of file, line and rule, a relative root or
        tests folder read from cwd, the working folder; whether the check passes, under strict too on the findings of
        its enforcement. Raises RootMissing, with the folder as given, when the app folder or the tests folder is no
        folder."""
        app, tested = cwd / root, (cwd / tests if tests is not None else None)
        absent = self._tree.absent(folder for folder in (app, tested) if folder is not None)
        if absent:
            raise RootMissing(root if absent[0] == app else tests)
        app, tested = self._tree.resolved(cwd, root), (self._tree.resolved(cwd, tests) if tests is not None else None)
        package = app.name
        checked = self._source.check(app, package, profile, tested)
        violations = ordered((*checked.violations, *self._structure.violations(app, package, profile, tested)))
        return AppChecked(violations, self._source.view(checked.enforcement), dict(checked.profile.hints),
                          passed(violations, checked.enforcement.strict, strict))
