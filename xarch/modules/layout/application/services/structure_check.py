from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.layout.application.logic.requirements import missing, requirements
from xarch.modules.layout.application.logic.unmirrored import unmirrored
from xarch.modules.layout.application.ports.disk import Disk
from xarch.modules.layout.application.ports.skeleton import Skeleton
from xarch.modules.layout.domain.structure import Repeated


class StructureCheckService:
    def __init__(self, disk: Disk, skeleton: Skeleton):
        self._disk, self._skeleton = disk, skeleton

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> list[Violation]:
        """What the layout requires and is missing below root, then every folder below the tests of each repeating
        folder that mirrors no folder of the app."""
        roots = self._skeleton.each_roots(profile)
        repeated = [Repeated(each, self._skeleton.each_parts(profile, each),
                             self._disk.subdirectories(root.joinpath(*each))) for each in roots]
        required = requirements(package, self._skeleton.top_level(profile), repeated,
                                self._skeleton.top_level_files(profile))
        present = {r for r in required if self._exists(root.joinpath(*r.path), r.is_dir)}
        found = missing(required, present)
        if tests is not None:
            for each in roots:
                app = set(self._disk.folders(root.joinpath(*each)))
                found += unmirrored(tests.absolute().name, package, each,
                                    self._disk.folders(tests.joinpath(*each)), app)
        return found

    def _exists(self, path: Path, is_dir: bool) -> bool:
        return self._disk.is_dir(path) if is_dir else self._disk.is_file(path)
