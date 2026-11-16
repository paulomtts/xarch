from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.spec.domain.values import Configured


class Settings(Protocol):
    """What the project around an app folder configured for xarch."""

    def configured_profile(self, app: Path) -> Configured | None:
        """The profile configured for the project holding app, given in full, or None; raises UnreadableSettings."""
        ...

    def configured_tests(self, app: Path) -> Path | None:
        """The tests root configured for the project holding app, given in full, relative paths resolved against the
        folder holding its pyproject.toml, or None; raises UnreadableSettings."""
        ...

    def configured_app(self, start: Path) -> Path | None:
        """The app folder configured for the project holding the folder start, given in full, looked up from start
        upward, a relative path resolved against the folder holding the pyproject.toml, or None; raises
        UnreadableSettings."""
        ...
