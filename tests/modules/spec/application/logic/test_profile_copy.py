"""What a copied profile may be called, where it goes and where the project records it."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.profile_copy import project_root, recorded, valid_name


@pytest.mark.parametrize("name, ok", [("mine", True), ("my-app_2", True), ("", False), ("a b", False),
                                      ("../x", False), ("a/b", False), ("-x", False), ("a.yaml", False)])
def test_a_name_is_letters_digits_dash_and_underscore_and_starts_with_a_letter_or_digit(name, ok):
    assert valid_name(name) is ok


def test_the_profile_is_recorded_relative_to_the_folder_holding_pyproject_as_posix():
    assert recorded(Path("/p/architecture/mine/mine.yaml"), Path("/p"), Path("/cwd")) == "architecture/mine/mine.yaml"
    assert recorded(Path("/other/mine.yaml"), Path("/p"), Path("/cwd")) == "../other/mine.yaml"


def test_the_project_is_the_folder_holding_the_app_folder():
    assert project_root(Path("/p/app")) == Path("/p")
