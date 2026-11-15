"""What scaffolding does to each file, and what lies at a path."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

CREATED = "created"
UPDATED = "updated"
SKIPPED = "skipped"

FILE = "file"
FOLDER = "folder"


@dataclass(frozen=True)
class Touched:
    """A file scaffolding reached, and what it did to it: CREATED, UPDATED, or SKIPPED because it already existed or
    already held what would be written."""
    path: Path
    done: str


@dataclass(frozen=True)
class Language:
    """The language of the app as scaffolding needs it: how a message names it, the file it has stand for each folder
    (which every folder of the skeleton holds), the words no name of an instance may be, what a name may be (a regular
    expression) and how a private one starts ("" for either: the language does not say)."""
    title: str
    package_file: str
    reserved: frozenset[str]
    names: str = ""
    private: str = ""

