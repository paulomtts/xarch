from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.outcomes import StructureFound


class Structure(Protocol):
    """What the layout of the profile in force finds wrong below an app folder."""

    def checked(self, root: Path, package: str, profile: str, tests: Path | None) -> StructureFound:
        """What the layout requires below root and is missing, then every folder below tests that mirrors no folder of
        the app, but what structure.accepted accepts, which is named apart; package names the app in each
        violation."""
        ...
