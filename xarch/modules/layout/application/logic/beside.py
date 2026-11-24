"""The test-tree rule under testing.beside: every test file below the tests root lies in a folder whose tests stay
there, a tier's `folder` or the fakes' folder; any other belongs beside the code it tests."""
from __future__ import annotations

from collections.abc import Iterable
from fnmatch import fnmatchcase

from xarch.kernel.logic.names import is_private_name
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.structure import Beside, Naming

STRAY = "lies below the tests folder, but testing.beside keeps the tests of a part beside its code"
STRAY_FIX = "move it beside the code it tests"


def stray(tests: str, files: Iterable[tuple[str, ...]], beside: Beside, naming: Naming) -> list[Violation]:
    """Every test file below the tests root, each given by its path below it, that lies in no folder beside keeps,
    sorted by path: a file whose name no pattern of beside matches is no test, and one in a folder whose name, or the
    name of a folder above it, is private in the language is never read; tests names the tests root in violations."""
    found: list[Violation] = []
    for path in sorted(files):
        if not path or any(is_private_name(step, naming.private) for step in path[:-1]):
            continue
        if not any(fnmatchcase(path[-1], pattern) for pattern in beside.files):
            continue
        if any(path[:len(folder)] == folder for folder in beside.kept):
            continue
        found.append(Violation("/".join((tests, *path)), 0, STRAY, "test-tree", STRAY_FIX))
    return found
