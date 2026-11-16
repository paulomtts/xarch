from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError


class InvalidName(DomainError):
    def __init__(self, name: str, language: str = ""):
        identifier = f"{language} identifier".lstrip()
        super().__init__(f"'{name}' is not a valid name: use a lowercase {identifier}, e.g. 'documents'")


class UnknownKind(DomainError):
    """A kind is the word one instance of the repeating folder is called; the profile declares no kind named so. word
    is the kind whose folder was given in its place, when it was ("" otherwise)."""

    def __init__(self, kind: str, known: Iterable[str], folders: dict[str, str] | None = None):
        known = list(known)
        self.kind = kind
        self.word = next((word for word, path in (folders or {}).items() if path == kind.strip("/")), "")
        if self.word:
            use = f"that is the folder of the kind {self.word}"
        else:
            use = f"use {', '.join(known)}" if known else "it declares no repeating folder"
        super().__init__(f"no kind '{kind}' in the profile: {use}")


class FolderMissing(DomainError):
    """The folder of a kind, which a new instance goes in, does not exist: the skeleton is not there."""

    def __init__(self, folder: Path):
        self.folder = folder
        super().__init__(f"{folder} does not exist")


class AlreadyExists(DomainError):
    """The instance to create is there already: its name, and its folder."""

    def __init__(self, name: str, base: Path):
        self.name, self.base = name, base
        super().__init__(f"'{name}' already exists at {base}")


class ProfileUnusable(DomainError):
    """The profile cannot give what `init` writes; reason says why, as the spec module put it."""
