"""What a copied profile may be called, where it goes and where the project records it."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.profile_copy import (
    conversion_refusal,
    copy_refusal,
    name_refusal,
    recorded,
    unnamed_refusal,
    valid_name,
)


@pytest.mark.parametrize("name, ok", [("mine", True), ("my-app_2", True), ("", False), ("a b", False),
                                      ("../x", False), ("a/b", False), ("-x", False), ("a.yaml", False)])
def test_a_name_is_letters_digits_dash_and_underscore_and_starts_with_a_letter_or_digit(name, ok):
    assert valid_name(name) is ok


def test_the_profile_is_recorded_relative_to_the_folder_holding_pyproject_as_posix():
    assert recorded(Path("/p/architecture/mine/mine.yaml"), Path("/p"), Path("/cwd")) == "architecture/mine/mine.yaml"
    assert recorded(Path("/other/mine.yaml"), Path("/p"), Path("/cwd")) == "../other/mine.yaml"



def test_a_name_that_is_no_profile_name_is_refused_with_what_a_name_may_be():
    assert name_refusal("my profile") == ("'my profile' is not a profile name: use letters, digits, '-' and '_', starting "
                                          "with a letter or a digit")


def test_a_copy_that_does_not_load_is_refused_with_every_problem_then_what_was_not_converted():
    assert copy_refusal(["a", "b"]) == "the copy does not load:\n  a\n  b"
    assert conversion_refusal(["a"], ["c"]) == "the converted profile does not load:\n  a\nnot converted:\n  c"
    assert conversion_refusal(["a"], []) == "the converted profile does not load:\n  a"


def test_a_bundled_profile_with_no_name_line_is_refused_saying_so():
    assert unnamed_refusal("cli") == "the bundled profile 'cli' has no `name` line to rename"
