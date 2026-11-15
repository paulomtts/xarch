from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError


class InvalidName(DomainError):
    def __init__(self, name: str):
        super().__init__(f"'{name}' is not a valid name: use a lowercase Python identifier, e.g. 'documents'")


class UnknownKind(DomainError):
    """A kind is a folder of the layout that declares `each:`; the profile declares no folder named so."""

    def __init__(self, kind: str, known: Iterable[str]):
        known = list(known)
        use = f"use {', '.join(known)}" if known else "it declares no folder with `each:`"
        super().__init__(f"no kind '{kind}' in the profile: {use}")


class FolderMissing(DomainError):
    def __init__(self, folder: Path):
        super().__init__(f"{folder} does not exist: run 'xarch init' first")


class AlreadyExists(DomainError):
    def __init__(self, name: str, base: Path):
        super().__init__(f"'{name}' already exists at {base}")
