"""What the rules module promises: check the imports below a root folder against section 5."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.violations import Violation


@dataclass(frozen=True)
class CheckImports:
    root: Path
    package: str = "app"           # the import name of the root folder
    profile: str = "cli"           # the skeleton profile; it names the entry-point folder


@dataclass(frozen=True)
class ImportsChecked:
    violations: tuple[Violation, ...]


@dataclass(frozen=True)
class NotADirectory:
    root: Path


CheckResult = ImportsChecked | NotADirectory
