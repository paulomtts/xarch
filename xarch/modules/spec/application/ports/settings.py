from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.spec.domain.values import Configured


class Settings(Protocol):
    """What the project around an app folder configured for xarch."""

    def configured_profile(self, app: Path) -> Configured | None:
        """The profile configured for the project holding app, or None; raises UnreadableSettings."""
        ...
