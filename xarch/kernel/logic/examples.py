"""Which file of an example project is test code: one whose path, below the folder holding the app, starts with the
folder of the tests (tests/<path>); every other file of it is the app's. Spec reads a profile's examples so, and rules
the examples of a check of the profile's own."""
from __future__ import annotations


def is_test_example(path: tuple[str, ...], tests: str) -> bool:
    """Whether the file of an example project at path is test code: its first step is the folder of the tests."""
    return bool(path) and path[0] == tests
