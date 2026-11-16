"""Where the app folder and the tests folder are, and the language of the app, when the project says nothing."""
from pathlib import Path

from xarch.modules.spec.application.logic.defaults import default_app, default_tests, first_language


def test_the_app_folder_is_app_in_the_working_folder():
    assert default_app() == Path("app")


def test_the_tests_folder_is_tests_beside_the_app_folder():
    assert default_tests(Path("/src/shop")) == Path("/src/tests")


def test_the_language_of_an_app_is_the_first_by_name_and_none_when_xarch_reads_none():
    assert (first_language({"python": 1, "pascal": 2}), first_language({})) == ("pascal", "")
