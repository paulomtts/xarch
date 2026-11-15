"""A file `init` writes beside the app folder: spec fills it from the profile, scaffold writes it and the rules module
compares a pinned one with what is there."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectFile:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules<ending>"); a file inside the app
        folder starts with the app folder's name
    content: the file's text, the app folder's name filled in, or, for a file that is not filled, its bytes as they are
    pinned: the project keeps it as written; `check` reports it when it differs
    preset: it comes from a folder entry of the profile
    """
    path: tuple[str, ...]
    content: str | bytes
    pinned: bool = False
    preset: bool = False
