"""In-memory implementation of spec's Settings port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.values import Configured


class FakeSettings:
    """Satisfies spec's Settings: a fixed configured profile, tests root and app folder (or none), or a fixed failure,
    for the project holding the app folder at (every app folder when at is None); any other folder has nothing
    configured. The app folder is configured for the project holding the folder asked from: from_folder when given,
    else any."""

    def __init__(self, configured: Configured | None = None, error: Exception | None = None,
                 tests: Path | None = None, at: Path | None = None, app: Path | None = None,
                 from_folder: Path | None = None):
        self._configured, self._error, self._tests, self._at = configured, error, tests, at
        self._app, self._from = app, from_folder

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

    def configured_app(self, start: Path) -> Path | None:
        if self._from is not None and start != self._from:
            return None
        if self._error:
            raise self._error
        return self._app

    def _holds(self, app: Path) -> bool:
        return self._at is None or app == self._at
