"""What the layout module promises: check that the skeleton of section 1 exists below a root folder.

It requires what the profile demands and ignores anything extra."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.published import Waived

__all__ = ["CheckStructure", "StructureChecked", "StructureRefused", "StructureResult", "Waived"]


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
    """What the layout finds wrong, the findings an entry of structure.accepted or of a counterpart's accepted
    accepts, which it does not report, and how many matches of its source each counterpart read, by its id."""
    violations: tuple[Violation, ...]
    waived: tuple[Waived, ...] = ()
    counterparts: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class StructureRefused:
    """The structure cannot be checked against the profile; reason is safe to show the user as-is."""
    reason: str


StructureResult = StructureChecked | StructureRefused
