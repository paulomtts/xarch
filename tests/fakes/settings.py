"""In-memory implementation of spec's Settings port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.values import Configured


class FakeSettings:
    """Satisfies spec's Settings: a fixed configured profile (or none), or a fixed failure."""

    def __init__(self, configured: Configured | None = None, error: Exception | None = None):
        self._configured, self._error = configured, error
        self.asked: list[Path] = []

    def configured_profile(self, app: Path) -> Configured | None:
        self.asked.append(app)
        if self._error:
            raise self._error
        return self._configured
