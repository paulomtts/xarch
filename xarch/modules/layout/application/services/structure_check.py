from __future__ import annotations

from pathlib import Path

from xarch.modules.layout.application.logic.allowed import sifted
from xarch.modules.layout.application.logic.beside import stray
from xarch.modules.layout.application.logic.counterparts import paired
from xarch.modules.layout.application.logic.requirements import anchors, missed, missing, requirements
from xarch.modules.layout.application.logic.unmirrored import unmirrored
from xarch.modules.layout.application.ports.disk import Disk
from xarch.modules.layout.application.ports.skeleton import Skeleton
from xarch.modules.layout.contract import StructureChecked
from xarch.modules.layout.domain.structure import Repeated, Requirement


class StructureCheckService:
    def __init__(self, disk: Disk, skeleton: Skeleton):
        self._disk, self._skeleton = disk, skeleton

    def check(self, root: Path, package: str, profile: str, tests: Path | None = None) -> StructureChecked:
        """What the layout requires and is missing below root, then every folder below the tests of each repeating
        folder that mirrors no folder of the app; under testing.beside, every test file below the tests that lies in no
        folder whose tests stay there instead; root and tests are given in full. A finding an entry of
        structure.accepted names is not reported but waived, and an entry that names none is a finding itself. Then
        what the counterparts find (see counterparts), the files of the app and of the tests read only when the
        profile writes one."""
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

        def there(steps: tuple[str, ...]) -> bool:
            return bool(self._disk.present(root, [Requirement("", steps, True, ""), Requirement("", steps, False, "")]))

        if tests is None:
            return self._paired(StructureChecked(*sifted(list(zip(at, found)), accepted, package, None, there)), root,
                                package, profile, None)
        beside = self._skeleton.beside(profile)
        if beside is not None:
            found += stray(tests.name, self._disk.files(tests), beside, naming)
        else:
            for each in roots:
                found += unmirrored(tests.name, package, each, self._disk.below(tests, each),
                                    set(self._disk.below(root, each)), naming)
        at += [(tuple(v.file.split("/")[1:]), True) for v in found[len(at):]]
        return self._paired(StructureChecked(*sifted(list(zip(at, found)), accepted, package, tests.name, there)), root,
                            package, profile, tests)

    def _paired(self, checked: StructureChecked, root: Path, package: str, profile: str,
                tests: Path | None) -> StructureChecked:
        """What the layout found, with what the counterparts find after it."""
        entries = self._skeleton.counterparts(profile)
        if not entries:
            return checked
        violations, waived, read = paired(entries, self._disk.files(root), self._disk.files(tests) if tests is not None else None,
                       self._skeleton.words(profile), self._skeleton.naming(profile), package,
                       tests.name if tests is not None else None)
        return StructureChecked((*checked.violations, *violations), (*checked.waived, *waived), read)

