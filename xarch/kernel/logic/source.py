"""What a source file says as its language's reader records it, in terms no language owns: the rules module checks
the app's imports with it, spec checks its examples' imports with it."""
from __future__ import annotations

from xarch.kernel.source import Import


def imported_module(imp: Import, folder: tuple[str, ...], root: str) -> tuple[str, ...] | None:
    """The steps, below the root package root, of the module an import names it from, folder being the importing
    file's folder below that root: from the folder when the import names names from it relatively, else from the top
    when its first step is root; None when it points outside the root."""
    if imp.relative and imp.names is not None:
        return relative_target(imp, folder)
    return imp.module[1:] if imp.module[:1] == (root,) else None


def relative_target(imp: Import, folder: tuple[str, ...]) -> tuple[str, ...] | None:
    """The steps, below the root the importing file's folder lies in, of the module a relative import names; None when
    it climbs above that root."""
    keep = len(folder) - imp.up
    return None if keep < 0 else folder[:keep] + imp.module
