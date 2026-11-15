"""In-memory implementation of spec's Settings port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.values import Configured


class FakeSettings:
    """Satisfies spec's Settings: a fixed configured profile and tests root (or none), or a fixed failure."""

    def __init__(self, configured: Configured | None = None, error: Exception | None = None,
                 tests: Path | None = None):
        self._configured, self._error, self._tests = configured, error, tests
        self.asked: list[Path] = []

    def configured_profile(self, app: Path) -> Configured | None:
        self.asked.append(app)
        if self._error:
            raise self._error
        return self._configured

    def configured_tests(self, app: Path) -> Path | None:
        if self._error:
            raise self._error
        return self._tests
