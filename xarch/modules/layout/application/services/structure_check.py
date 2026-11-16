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
        folder that mirrors no folder of the app; root and tests are given in full."""
        roots = self._skeleton.each_roots(profile)
        repeated = [Repeated(each, self._skeleton.each_parts(profile, each),
                             self._disk.instances(root, each)) for each in roots]
        naming = self._skeleton.naming(profile)
        required = requirements(package, self._skeleton.top_level(profile), repeated,
                                self._skeleton.top_level_files(profile), naming)
        found = missing(required, self._disk.present(root, required))
        if tests is not None:
            for each in roots:
                found += unmirrored(tests.name, package, each, self._disk.below(tests, each),
                                    set(self._disk.below(root, each)), naming)
        return found

