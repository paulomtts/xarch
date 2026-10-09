"""Values of the spec module."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Configured:
    """A profile name as a project configured it, and the file it came from."""
    name: str
    source: Path
