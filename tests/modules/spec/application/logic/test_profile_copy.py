"""The text of a copied profile: named for the copy and based on what it was copied from; where it is recorded."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.profile_copy import copied_text, project_root, recorded, valid_name

ORIGINAL = "# a comment\nxarch: 2\nname: web\nlanguage: python\n\nparts:\n  name: not this one\n"


def test_the_copy_is_named_and_based_on_the_original_and_keeps_everything_else_as_written():
    assert copied_text(ORIGINAL, "mine", "web") == (
        "# a comment\nxarch: 2\nname: mine\nbased_on: web\nlanguage: python\n\nparts:\n  name: not this one\n")


def test_a_based_on_the_original_already_had_is_replaced_not_repeated():
    text = copied_text("xarch: 2\nname: web\nbased_on: cli\n", "mine", "web")
    assert text == "xarch: 2\nname: mine\nbased_on: web\n"


def test_a_profile_with_no_name_line_cannot_be_copied():
    assert copied_text("xarch: 2\nparts: {}\n", "mine", "web") is None


@pytest.mark.parametrize("name, ok", [("mine", True), ("my-app_2", True), ("", False), ("a b", False),
                                      ("../x", False), ("a/b", False), ("-x", False), ("a.yaml", False)])
def test_a_name_is_letters_digits_dash_and_underscore_and_starts_with_a_letter_or_digit(name, ok):
    assert valid_name(name) is ok


def test_the_profile_is_recorded_relative_to_the_folder_holding_pyproject_as_posix():
    assert recorded(Path("/p/architecture/mine/mine.yaml"), Path("/p"), Path("/cwd")) == "architecture/mine/mine.yaml"
    assert recorded(Path("/other/mine.yaml"), Path("/p"), Path("/cwd")) == "../other/mine.yaml"


def test_the_project_is_the_folder_holding_the_app_folder():
    assert project_root(Path("/p/app")) == Path("/p")
