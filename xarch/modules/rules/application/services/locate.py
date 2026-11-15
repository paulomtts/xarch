from __future__ import annotations

from xarch.modules.rules.application.logic.where import candidates, describe, resolve
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import Locate
from xarch.modules.rules.domain.errors import OutsideProject
from xarch.modules.rules.domain.values import Placed


class LocateService:
    """Says what a path is, and what code there may do, before any is written."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def locate(self, cmd: Locate) -> Placed:
        """What the path is, placed or not; raises OutsideProject for a path outside the project."""
        app = self._tree.resolved(cmd.app)
        tests = self._tree.resolved(cmd.tests) if cmd.tests is not None else None
        existing = self._tree.existing(candidates(cmd.path, cmd.cwd, app))
        found = resolve(cmd.path, cmd.cwd, app, tests, existing)
        if found is None:
            raise OutsideProject(cmd.path, app.parent)
        return describe(self._profiles.profile(cmd.profile), found, app, tests)
