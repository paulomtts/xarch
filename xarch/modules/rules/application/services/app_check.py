from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.domain.values import Checked


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, tree: SourceTree):
        self._source, self._structure, self._tree = source, structure, tree

    def check(self, root: Path, profile: str, tests: Path | None) -> Checked:
        """The violations of the source, then of the structure; raises RootMissing when the app folder or the tests
        folder is no folder."""
        package = self._tree.resolved(root).name
        checked = self._source.check(root, package, profile, tests)
        structure = self._structure.violations(root, package, profile, tests)
        return replace(checked, violations=(*checked.violations, *structure))
