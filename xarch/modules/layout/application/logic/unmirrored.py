"""The test-tree rule: every folder below the tests of a repeating folder mirrors a folder of the app."""
from __future__ import annotations

from collections.abc import Collection, Iterable

from xarch.kernel.logic.names import is_private_name
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.structure import Naming


def _hidden(path: tuple[str, ...], naming: Naming) -> bool:
    """A folder whose name, or the name of a folder above it, is private in the language (such as one of compiled
    files), which mirrors nothing and is never checked."""
    return any(is_private_name(step, naming.private) for step in path)


def unmirrored(tests: str, root: str, each_root: tuple[str, ...], folders: Iterable[tuple[str, ...]],
               app: Collection[tuple[str, ...]], naming: Naming) -> list[Violation]:
    """Every folder below the tests of a repeating folder (tests/<its root>/) that mirrors no folder of the app.

    folders are below tests/<each root>/, app the app's folders below <each root>/; tests and root name the two
    roots in violations."""
    found: list[Violation] = []
    for folder in sorted(folders):
        if _hidden(folder, naming) or folder in app:
            continue
        mirrored = "/".join((root, *each_root, *folder))
        found.append(Violation("/".join((tests, *each_root, *folder)), 0,
                               f"mirrors no folder of the app ({mirrored})", "test-tree",
                               f"create {mirrored}/ in the app, or move what it holds to the folder that mirrors its "
                               "subject, or remove it"))
    return found
