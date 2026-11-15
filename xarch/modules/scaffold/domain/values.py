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
