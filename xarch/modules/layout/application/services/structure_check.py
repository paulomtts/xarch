from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.layout.application.ports.disk import Disk
from xarch.modules.layout.application.ports.skeleton import Skeleton
from xarch.modules.layout.domain.structure import missing, requirements


class StructureCheck:
    def __init__(self, disk: Disk, skeleton: Skeleton):
        self._disk, self._skeleton = disk, skeleton

    def check(self, root: Path, package: str, profile: str) -> list[Violation]:
        modules = self._disk.subdirectories(root / "modules")                                    # load
        required = requirements(package, self._skeleton.top_level(profile),
                                self._skeleton.module_parts(profile), modules)
        present = {r for r in required if self._exists(root.joinpath(*r.path), r.is_dir)}
        return missing(required, present)

    def _exists(self, path: Path, is_dir: bool) -> bool:
        return self._disk.is_dir(path) if is_dir else self._disk.is_file(path)
