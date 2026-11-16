"""Where the app folder and the tests folder are, and which language the app is in, when the project says nothing."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.modules.spec.domain.published import DEFAULT_APP, DEFAULT_TESTS


def default_app() -> Path:
    """The app folder, in the working folder."""
    return Path(DEFAULT_APP)


def default_tests(app: Path) -> Path:
    """The tests folder beside the app folder, which app names from the root down."""
    return app.parent / DEFAULT_TESTS


def first_language(languages: Iterable[str]) -> str:
    """The language of an app whose profile names none: the first of the languages xarch reads, by name; "" when it
    reads none."""
    return min(languages, default="")
