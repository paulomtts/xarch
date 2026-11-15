"""In-memory implementation of spec's Settings port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.values import Configured


class FakeSettings:
    """Satisfies spec's Settings: a fixed configured profile and tests root (or none), or a fixed failure, for the
    project holding the app folder at (every app folder when at is None); any other folder has nothing configured."""

    def __init__(self, configured: Configured | None = None, error: Exception | None = None,
                 tests: Path | None = None, at: Path | None = None):
        self._configured, self._error, self._tests, self._at = configured, error, tests, at

    def configured_profile(self, app: Path) -> Configured | None:
        if not self._holds(app):
            return None
        if self._error:
            raise self._error
        return self._configured

    def configured_tests(self, app: Path) -> Path | None:
        if not self._holds(app):
            return None
        if self._error:
            raise self._error
        return self._tests

    def _holds(self, app: Path) -> bool:
        return self._at is None or app == self._at
