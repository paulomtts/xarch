"""Where a project's folders are when it says nothing: the project is the folder holding the app folder; the app
folder is app/ in the folder a command starts from, and the tests folder is tests/ in the project."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.published import DEFAULT_APP, DEFAULT_TESTS


def project_root(app: Path) -> Path:
    """The folder holding the app folder: the project's, where pyproject.toml records a profile and a copy goes."""
    return app.parent


def default_app(start: Path) -> Path:
    """The app folder of a project that records none: app/ in start, the folder the command starts from, in full."""
    return start / DEFAULT_APP


def default_tests(app: Path) -> Path:
    """The tests folder of a project that records none: tests/ in the project of the app folder."""
    return project_root(app) / DEFAULT_TESTS
