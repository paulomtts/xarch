from __future__ import annotations

from pathlib import Path

from xarch.modules.layout.application.logic.allowed import sifted
from xarch.modules.layout.application.logic.beside import stray
from xarch.modules.layout.application.logic.requirements import anchors, missed, missing, requirements
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
        folder whose tests stay there instead; root and tests are given in full. A finding an entry of
        structure.accepted names is not reported but waived, and an entry that names none is a finding itself."""
        roots = self._skeleton.each_roots(profile)
        repeated = [Repeated(each, self._skeleton.each_parts(profile, each),
                             self._disk.instances(root, each), self._skeleton.when(profile, each)) for each in roots]
        naming = self._skeleton.naming(profile)
        required = requirements(package, self._skeleton.top_level(profile), repeated,
                                self._skeleton.top_level_files(profile), naming, self._skeleton.when(profile))
        present = self._disk.present(root, [*required, *anchors(required)])
        found = missing(required, present)
        at = [(r.path, False) for r in missed(required, present)]
        accepted = self._skeleton.accepted(profile)
        if tests is None:
            return StructureChecked(*sifted(list(zip(at, found)), accepted, package, None))
        beside = self._skeleton.beside(profile)
        if beside is not None:
            found += stray(tests.name, self._disk.files(tests), beside, naming)
        else:
            for each in roots:
                found += unmirrored(tests.name, package, each, self._disk.below(tests, each),
                                    set(self._disk.below(root, each)), naming)
        at += [(tuple(v.file.split("/")[1:]), True) for v in found[len(at):]]
        return StructureChecked(*sifted(list(zip(at, found)), accepted, package, tests.name))

