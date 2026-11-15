from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.kernel.violations import Violation


class Structure(Protocol):
    """What the layout of the profile in force finds wrong below an app folder."""

    def violations(self, root: Path, package: str, profile: str, tests: Path | None) -> list[Violation]:
        """What the layout requires below root and is missing, then every folder below tests that mirrors no folder of
        the app; package names the app in each violation."""
        ...
