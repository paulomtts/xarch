"""What a source file says as its language's reader records it, in terms no language owns: the rules module checks
the app's imports with it, spec checks its examples' imports with it."""
from __future__ import annotations

from xarch.kernel.source import Import


def relative_target(imp: Import, folder: tuple[str, ...]) -> tuple[str, ...] | None:
    """The steps, below the root the importing file's folder lies in, of the module a relative import names; None when
    it climbs above that root."""
    keep = len(folder) - imp.up
    return None if keep < 0 else folder[:keep] + imp.module
