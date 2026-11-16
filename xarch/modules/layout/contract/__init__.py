"""What the layout module promises: check that the skeleton of section 1 exists below a root folder.

It requires what the profile demands and ignores anything extra."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.violations import Violation


@dataclass(frozen=True)
class CheckStructure:
    """Check that the layout of the architecture at profile exists below root, named package in violations, and
    that the tests below tests (None: no tests) mirror the app's folders; root and tests are given in full."""
    root: Path
    package: str
    profile: str
    tests: Path | None = None


@dataclass(frozen=True)
class StructureChecked:
    violations: tuple[Violation, ...]
