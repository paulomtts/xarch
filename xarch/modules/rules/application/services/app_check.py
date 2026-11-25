from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.application.logic.chosen import chosen
from xarch.modules.rules.application.logic.ordered import ordered
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.contract import AppChecked, Partial
from xarch.modules.rules.domain.errors import RootMissing, StrictAgainst


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, tree: SourceTree):
        self._source, self._structure, self._tree = source, structure, tree

    def check(self, root: Path, profile: str, tests: Path | None, cwd: Path, strict: bool,
              against: str | None = None, paths: tuple[Path, ...] | None = None) -> AppChecked:
        """The violations of the source and of the structure, in order of file, line and rule, a relative root or
        tests folder read from cwd, the working folder; whether the check passes, under strict too on the findings of
        its enforcement. Raises StrictAgainst, before anything is looked at, when strict is asked with against, and
        RootMissing, with the folder as given, when the app folder or the tests folder is no folder. With paths, each
        read from cwd, every check still runs on the whole app and its tests, and the violations of files at or below
        them alone are shown and decide whether it passes; the others are counted."""
        if strict and against is not None:
            raise StrictAgainst()
        app, tested = cwd / root, (cwd / tests if tests is not None else None)
        absent = self._tree.absent(folder for folder in (app, tested) if folder is not None)
        if absent:
            raise RootMissing(root if absent[0] == app else tests)
        app, tested = self._tree.resolved(cwd, root), (self._tree.resolved(cwd, tests) if tests is not None else None)
        package = app.name
        checked = self._source.check(app, package, profile, tested)
        violations = ordered((*checked.violations, *self._structure.violations(app, package, profile, tested)))
        partial = None
        if paths is not None:
            places = [self._tree.resolved(cwd, path) for path in dict.fromkeys(paths)]
            violations, elsewhere = chosen(violations, places, app.parent, tested)
            partial = Partial(tuple(path.as_posix() for path in paths), elsewhere)
        return AppChecked(tuple(violations), self._source.view(checked.enforcement), dict(checked.profile.hints),
                          passed(violations, checked.enforcement.strict, strict), partial)
