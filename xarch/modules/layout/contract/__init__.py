"""What the layout module promises: check that the skeleton of section 1 exists below a root folder.

It requires what the profile demands and ignores anything extra."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.violations import Violation


@dataclass(frozen=True)
class CheckStructure:
    root: Path
    package: str = "app"           # names the root in violations
    profile: str = "cli"           # the skeleton profile whose folders must exist


@dataclass(frozen=True)
class StructureChecked:
    violations: tuple[Violation, ...]
