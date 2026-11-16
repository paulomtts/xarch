from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.domain.errors import RootMissing
from xarch.modules.rules.domain.values import Checked


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, tree: SourceTree):
        self._source, self._structure, self._tree = source, structure, tree

    def check(self, root: Path, profile: str, tests: Path | None, cwd: Path) -> Checked:
        """The violations of the source, then of the structure, a relative root or tests folder read from cwd, the
        working folder; raises RootMissing, with the folder as given, when the app folder or the tests folder is no
        folder."""
        app, tested = cwd / root, (cwd / tests if tests is not None else None)
        absent = self._tree.absent(folder for folder in (app, tested) if folder is not None)
        if absent:
            raise RootMissing(root if absent[0] == app else tests)
        app, tested = self._tree.resolved(cwd, root), (self._tree.resolved(cwd, tests) if tests is not None else None)
        package = app.name
        checked = self._source.check(app, package, profile, tested)
        structure = self._structure.violations(app, package, profile, tested)
        return replace(checked, violations=(*checked.violations, *structure))
