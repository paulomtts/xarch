from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.domain.values import LOWERCASE, NOT_A_NAME, PRIVATE, RESERVED


class InvalidName(DomainError):
    """A name of a new instance that breaks a rule of such names (one of scaffold's LOWERCASE, NOT_A_NAME, PRIVATE and
    RESERVED), said with which and what to write."""

    def __init__(self, name: str, rule: str, language: str = "", private: str = ""):
        identifier = f"{language} identifier".lstrip()
        why = {LOWERCASE: "use lowercase plain letters, as in 'documents'",
               NOT_A_NAME: f"it is no {identifier}: write one, such as 'documents'",
               PRIVATE: f"it is private, as a name starting with '{private}' is: drop the '{private}'",
               RESERVED: f"it is a word {language or 'the language'} reserves: choose another, such as 'documents'"}
        super().__init__(f"'{name}' is not a valid name: {why[rule]}")


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
