"""What a source file says as its language's reader records it, in terms no language owns: the rules module checks
the app's imports with it, spec checks its examples' imports with it."""
from __future__ import annotations

from xarch.kernel.source import Import


def _imported_module(imp: Import, folder: tuple[str, ...], root: str) -> tuple[str, ...] | None:
    """The steps, below the root package root, of the module an import names it from, folder being the importing
    file's folder below that root: from the folder when the import names names from it relatively, else from the top
    when its first step is root; None when it points outside the root."""
    if imp.relative and imp.names is not None:
        return _relative_target(imp, folder)
    return imp.module[1:] if imp.module[:1] == (root,) else None


def imported_names(imp: Import, folder: tuple[str, ...], root: str) -> list[tuple[tuple[str, ...], str | None]]:
    """What an import takes, below the root package root (see _imported_module): the module it names, with each name it
    takes from it, or None for the module taken as a whole; none when it points outside the root. Whether a name
    taken from a module is a module of its own, or a name the module defines, is the caller's to say."""
    base = _imported_module(imp, folder, root)
    if base is None:
        return []
    return [(base, None)] if imp.names is None else [(base, name) for name in imp.names]


def _relative_target(imp: Import, folder: tuple[str, ...]) -> tuple[str, ...] | None:
    """The steps, below the root the importing file's folder lies in, of the module a relative import names; None when
    it climbs above that root."""
    keep = len(folder) - imp.up
    return None if keep < 0 else folder[:keep] + imp.module
