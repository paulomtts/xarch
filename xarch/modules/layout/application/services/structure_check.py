from __future__ import annotations

from pathlib import Path

from xarch.modules.layout.application.logic.beside import stray
from xarch.modules.layout.application.logic.requirements import missing, requirements
from xarch.modules.layout.application.logic.unmirrored import unmirrored
from xarch.modules.layout.application.ports.disk import Disk
from xarch.modules.layout.application.ports.skeleton import Skeleton
from xarch.modules.layout.contract import StructureChecked
from xarch.modules.layout.domain.structure import Repeated


class StructureCheckService:
    def __init__(self, disk: Disk, skeleton: Skeleton):
        self._disk, self._skeleton = disk, skeleton

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> StructureChecked:
        """What the layout requires and is missing below root, then every folder below the tests of each repeating
        folder that mirrors no folder of the app; under testing.beside, every test file below the tests that lies in no
        folder whose tests stay there instead; root and tests are given in full."""
        roots = self._skeleton.each_roots(profile)
        repeated = [Repeated(each, self._skeleton.each_parts(profile, each),
                             self._disk.instances(root, each)) for each in roots]
        naming = self._skeleton.naming(profile)
        required = requirements(package, self._skeleton.top_level(profile), repeated,
                                self._skeleton.top_level_files(profile), naming)
        found = missing(required, self._disk.present(root, required))
        if tests is None:
            return StructureChecked(tuple(found))
        beside = self._skeleton.beside(profile)
        if beside is not None:
            found += stray(tests.name, self._disk.files(tests), beside, naming)
        else:
            for each in roots:
                found += unmirrored(tests.name, package, each, self._disk.below(tests, each),
                                    set(self._disk.below(root, each)), naming)
        return StructureChecked(tuple(found))

