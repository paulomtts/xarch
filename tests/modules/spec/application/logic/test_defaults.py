"""Where the app folder and the tests folder are when the project says nothing."""
from pathlib import Path

from xarch.modules.spec.application.logic.defaults import default_app, default_tests


def test_the_app_folder_is_app_in_the_working_folder():
    assert default_app() == Path("app")


def test_the_tests_folder_is_tests_beside_the_app_folder():
    assert default_tests(Path("/src/shop")) == Path("/src/tests")
