from __future__ import annotations

from xarch.modules.rules.application.logic.where import describe, resolve
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import Locate, Located, LocateResult, Outside


class Locator:
    """Says what a path is, and what code there may do, before any is written."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def locate(self, cmd: Locate) -> LocateResult:
        """The path outside the project is refused; anything inside it is described, placed or not."""
        app = cmd.app.absolute().resolve()
        tests = cmd.tests.absolute().resolve() if cmd.tests is not None else None
        found = resolve(cmd.path, cmd.cwd, app, tests, self._tree.exists)
        if found is None:
            return Outside(f"{cmd.path.as_posix()} lies outside the project: it is not below {app.parent.as_posix()}")
        return Located(describe(self._profiles.profile(cmd.profile), found, app, tests))
