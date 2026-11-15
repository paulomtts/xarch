from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError


class InvalidName(DomainError):
    def __init__(self, name: str, language: str = ""):
        identifier = f"{language} identifier".lstrip()
        super().__init__(f"'{name}' is not a valid name: use a lowercase {identifier}, e.g. 'documents'")


class UnknownKind(DomainError):
    """A kind is the word one instance of the repeating folder is called; the profile declares no kind named so."""

    def __init__(self, kind: str, known: Iterable[str], folders: dict[str, str] | None = None):
        known = list(known)
        folder = next((word for word, path in (folders or {}).items() if path == kind.strip("/")), None)
        if folder is not None:
            use = f"that is the folder of the kind {folder}: write `xarch new {folder} <name>`"
        else:
            use = f"use {', '.join(known)}" if known else "it declares no repeating folder"
        super().__init__(f"no kind '{kind}' in the profile: {use}")


class FolderMissing(DomainError):
    def __init__(self, folder: Path):
        super().__init__(f"{folder} does not exist: run 'xarch init' first")


class AlreadyExists(DomainError):
    def __init__(self, name: str, base: Path):
        super().__init__(f"'{name}' already exists at {base}")


class ProfileUnusable(DomainError):
    """The profile cannot give what `init` writes; reason says why, as the spec module put it."""
