from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.layout.application.ports.disk import Disk
from xarch.modules.layout.application.ports.skeleton import Skeleton
from xarch.modules.layout.domain.structure import missing, requirements, unmirrored


class StructureCheck:
    def __init__(self, disk: Disk, skeleton: Skeleton):
        self._disk, self._skeleton = disk, skeleton

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> list[Violation]:
        """What the layout requires and is missing below root, then every folder below the tests of the `each`
        folder that mirrors no folder of the app."""
        each_root = self._skeleton.each_root(profile)
        instances = self._disk.subdirectories(root.joinpath(*each_root)) if each_root is not None else []
        required = requirements(package, self._skeleton.top_level(profile), each_root,
                                self._skeleton.each_parts(profile), instances)
        present = {r for r in required if self._exists(root.joinpath(*r.path), r.is_dir)}
        found = missing(required, present)
        if tests is not None and each_root is not None:
            app = set(self._disk.folders(root.joinpath(*each_root)))
            found += unmirrored(tests.absolute().name, package, each_root,
                                self._disk.folders(tests.joinpath(*each_root)), app)
        return found

    def _exists(self, path: Path, is_dir: bool) -> bool:
        return self._disk.is_dir(path) if is_dir else self._disk.is_file(path)
