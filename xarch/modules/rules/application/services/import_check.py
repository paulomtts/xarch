from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.ports.skeleton import Skeleton
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import RootMissing
from xarch.modules.rules.domain.imports import violations


class ImportCheck:
    def __init__(self, tree: SourceTree, skeleton: Skeleton):
        self._tree, self._skeleton = tree, skeleton

    def check(self, root: Path, package: str, profile: str) -> list[Violation]:
        if not self._tree.is_dir(root):
            raise RootMissing(root)                                  # precondition: the root must exist
        return violations(self._tree.read(root), self._skeleton.parts(profile), package)
