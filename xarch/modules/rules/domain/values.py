"""The values the import rules reason about: the layout's folder names and already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Parts:
    """The folder names that give code its place: below the app root, below a module, below application/."""
    top_level: frozenset[str]           # kernel, platform, bootstrap (not modules, not the entry point)
    module_folders: frozenset[str]      # contract, domain, adapters (not application)
    application_parts: frozenset[str]   # controller, services, logic, ports
    entry_point: str                    # the folder that drives the modules: cli or web, by profile


@dataclass(frozen=True)
class Import:
    """One imported name as written. names is None for `import a.b`, the imported names for `from a import x`."""
    line: int
    module: tuple[str, ...]
    level: int = 0
    names: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SourceFile:
    name: str                    # how the file is shown, e.g. "app/kernel/x.py"
    path: tuple[str, ...]        # below the root, e.g. ("kernel", "x.py")
    imports: tuple[Import, ...]
