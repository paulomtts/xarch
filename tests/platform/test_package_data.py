"""The data files shipped inside a package: the files of a folder, every file below one, and their content."""
import pytest

from xarch.platform.package_data import PackageData

BUNDLED = PackageData("xarch", "architectures")


def test_the_files_directly_in_a_folder_are_named_sorted_and_none_in_what_is_no_folder():
    assert {"cli.yaml", "web.yaml"} <= set(BUNDLED.files_in())
    assert BUNDLED.files_in() == sorted(BUNDLED.files_in())
    assert BUNDLED.files_in("presets/testing") == ["pytest.yaml"]
    assert BUNDLED.files_in("nowhere") == []


def test_every_file_below_a_folder_is_listed_by_its_path_in_it_and_none_below_what_is_no_folder():
    below = BUNDLED.files_below("presets")
    assert "testing/pytest.yaml" in below and below == sorted(below)
    assert BUNDLED.files_below("nowhere") == []


def test_a_file_is_read_as_text_or_bytes_and_a_missing_one_raises():
    assert BUNDLED.is_file("cli.yaml") and not BUNDLED.is_file("presets")
    assert BUNDLED.read_text("cli.yaml").startswith(BUNDLED.read_bytes("cli.yaml").decode("utf-8")[:20])
    with pytest.raises(FileNotFoundError):
        BUNDLED.read_text("nowhere.yaml")
