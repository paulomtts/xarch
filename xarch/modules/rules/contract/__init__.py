"""What the rules module promises: check the imports below a root folder against section 5."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import (
    At,
    Drift,
    Enforcement,
    Excluded,
    Finding,
    Loosened,
    Nearest,
    Origin,
    Reach,
    TierInfo,
    Weak,
    Where,
)

__all__ = ["At", "Drift", "Enforcement", "Excluded", "Finding", "Loosened", "Nearest", "Origin", "Reach", "TierInfo", "Weak",
           "Where", "CheckImports", "ImportsChecked", "NotADirectory", "CheckResult", "Locate", "Located", "Outside",
           "LocateResult"]


@dataclass(frozen=True)
class CheckImports:
    """Check the code below root, imported as package, and the tests below tests (None: no tests), against the
    architecture at profile (a bundled name or a path)."""
    root: Path
    package: str
    profile: str
    tests: Path | None = None


@dataclass(frozen=True)
class ImportsChecked:
    """The violations, in the order the checks found them, and the state of the check's own enforcement."""
    violations: tuple[Violation, ...]
    enforcement: Enforcement = Enforcement()


@dataclass(frozen=True)
class NotADirectory:
    root: Path


CheckResult = ImportsChecked | NotADirectory


@dataclass(frozen=True)
class Locate:
    """Say what the path is and what code there may do. path is given from cwd, from the folder holding app, or from
    app; it may not exist yet. tests is the tests root (None: none), profile the architecture in force."""
    path: Path
    cwd: Path
    app: Path
    profile: str
    tests: Path | None = None


@dataclass(frozen=True)
class Located:
    where: Where


@dataclass(frozen=True)
class Outside:
    """The path is not in the project; reason is safe to show the user as-is."""
    reason: str


LocateResult = Located | Outside
