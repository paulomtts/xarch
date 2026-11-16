"""Where a project's folders are when it says nothing: the project holds the app folder, the app folder is app/ in the
folder a command starts from, and the tests folder is tests/ in the project."""
from pathlib import Path

from xarch.modules.spec.application.logic.project_folders import default_app, default_tests, project_root


def test_the_project_is_the_folder_holding_the_app_folder():
    assert project_root(Path("/p/app")) == Path("/p")


def test_the_app_folder_is_app_in_the_folder_the_command_starts_from():
    assert default_app(Path("/work")) == Path("/work/app")


def test_the_tests_folder_is_tests_beside_the_app_folder():
    assert default_tests(Path("/src/shop")) == Path("/src/tests")
