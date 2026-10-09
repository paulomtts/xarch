from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError


class InvalidModuleName(DomainError):
    def __init__(self, name: str):
        super().__init__(f"'{name}' is not a valid module name: use a lowercase Python identifier, e.g. 'documents'")


class ModulesFolderMissing(DomainError):
    def __init__(self, modules: Path):
        super().__init__(f"{modules} does not exist: run 'xarch init' first")


class ModuleExists(DomainError):
    def __init__(self, name: str, base: Path):
        super().__init__(f"module '{name}' already exists at {base}")
