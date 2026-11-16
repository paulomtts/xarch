"""Where the app folder and the tests folder are when the project says nothing."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.published import DEFAULT_APP

TESTS = "tests"
"""The folder of the tests, beside the app folder, when none is given or configured."""


def default_app() -> Path:
    """The app folder, in the working folder."""
    return Path(DEFAULT_APP)


def default_tests(app: Path) -> Path:
    """The tests folder beside the app folder, which app names from the root down."""
    return app.parent / TESTS
