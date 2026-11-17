"""Spec's ArchitectureFiles: a bundled profile read from the package data, any other from the disk, with the files
beside it; a file that cannot be read is an invalid architecture naming it."""
import pytest

from xarch.modules.spec.adapters.fs_architecture_files import FsArchitectureFiles
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureSource
from xarch.platform.data_files import DataFileReader
from xarch.platform.filesystem import FileSystem
from xarch.platform.package_data import PackageData

BUNDLED = ArchitectureSource("cli", bundled=True)


def files() -> FsArchitectureFiles:
    return FsArchitectureFiles(FileSystem(), DataFileReader(), PackageData("xarch", "architectures"))


def test_the_bundled_profiles_and_the_testing_presets_come_from_the_package_data():
    assert files().bundled() == ("cli", "web")
    assert list(files().testing_presets()) == ["pytest"]
    assert files().read(BUNDLED).source == "cli.yaml" and files().read(BUNDLED).document["name"] == "cli"
    assert "\nname: cli\n" in files().profile_text(BUNDLED)
    assert files().has_file(BUNDLED, "cli.md") and not files().has_file(BUNDLED, "nowhere.md")


def test_a_profile_on_disk_is_read_with_the_files_beside_it(tmp_path):
    (tmp_path / "mine.yaml").write_text("name: mine\n")
    (tmp_path / "kit" / "deep").mkdir(parents=True)
    (tmp_path / "kit" / "a.txt").write_text("a")
    (tmp_path / "kit" / "deep" / "b.bin").write_bytes(b"\xff")
    source = ArchitectureSource(str(tmp_path / "mine.yaml"), bundled=False)
    assert files().read(source).document == {"name": "mine"}
    assert files().profile_text(source) == "name: mine\n"
    assert files().files_under(source, "kit") == ("a.txt", "deep/b.bin")
    assert (files().read_text(source, "kit/a.txt"), files().read_bytes(source, "kit/deep/b.bin")) == ("a", b"\xff")
    assert files().has_file(source, "kit/a.txt") and not files().has_file(source, "kit")


def test_what_cannot_be_read_is_an_invalid_architecture_naming_the_file(tmp_path):
    (tmp_path / "bad.yaml").write_text("a: [")
    (tmp_path / "bin.md").write_bytes(b"\xff\xfe")
    bad = ArchitectureSource(str(tmp_path / "bad.yaml"), bundled=False)
    with pytest.raises(InvalidArchitecture) as parsed:
        files().read(bad)
    with pytest.raises(InvalidArchitecture) as text:
        files().read_text(bad, "bin.md")
    with pytest.raises(InvalidArchitecture) as missing:
        files().read_bytes(bad, "gone.md")
    assert parsed.value.problems[0].startswith(f"{bad.location}: not valid YAML")
    assert text.value.problems == (f"{bad.location}: cannot read 'bin.md': it is not valid UTF-8 text",)
    assert missing.value.problems == (f"{bad.location}: cannot read 'gone.md': No such file or directory",)


class BrokenPackage(PackageData):
    """The package data with one file whose text is not a valid data file."""

    def __init__(self, broken: str, text: str):
        super().__init__("xarch", "architectures")
        self._broken, self._text = broken, text

    def read_text(self, relative: str) -> str:
        return self._text if relative == self._broken else super().read_text(relative)


def test_the_data_files_of_the_format_come_from_the_package_data():
    document = files().format_keys()
    assert list(document) == ["fragments", "smallest", "symbols", "keys", "slots"]
    assert document["keys"]["name"] == {"meaning": "what the profile is called", "accepts": "a non-empty string",
                                        "example": "name: documents-app"}
    assert files().file_types()[".sql"] == {"comment": "--"}


@pytest.mark.parametrize("path, read", [("presets/format/keys.yaml", "format_keys"),
                                        ("presets/format/file_types.yaml", "file_types")])
def test_a_data_file_that_does_not_parse_is_an_invalid_architecture_naming_it(path, read):
    broken = FsArchitectureFiles(FileSystem(), DataFileReader(), BrokenPackage(path, "keys: ["))
    with pytest.raises(InvalidArchitecture) as caught:
        getattr(broken, read)()
    assert caught.value.problems == (f"{path}: cannot read the data file: not valid YAML: line 1, column 8: expected the "
                                     "node content, but found '<stream end>'",)
