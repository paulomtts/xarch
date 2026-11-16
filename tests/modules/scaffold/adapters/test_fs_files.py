"""FsFiles on real files: what lies at a path, a file laid down as text, empty or bytes, and the nearest pyproject.toml."""
from pathlib import Path

import pytest

from xarch.modules.scaffold.adapters.fs_files import FsFiles
from xarch.modules.scaffold.domain.values import FILE, FOLDER
from xarch.platform.filesystem import FileSystem


def files() -> FsFiles:
    return FsFiles(FileSystem())


def test_kind_tells_a_folder_from_a_file_and_from_nothing(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    assert (files().kind(tmp_path), files().kind(tmp_path / "a.txt"), files().kind(tmp_path / "none")) == \
        (FOLDER, FILE, None)


@pytest.mark.parametrize("content", [
    pytest.param("", id="empty text makes an empty file"),
    pytest.param("all: app\n", id="other text is written as text"),
])
def test_lay_down_writes_text_creating_the_folders_above(tmp_path, content):
    path = tmp_path / "a" / "b" / "c.txt"
    files().lay_down(path, content)
    assert path.read_text() == content


def test_lay_down_writes_bytes_as_they_are(tmp_path):
    path = tmp_path / "a" / "logo.woff"
    files().lay_down(path, b"\xff\x00")
    assert path.read_bytes() == b"\xff\x00"


def test_lay_down_replaces_what_a_file_held(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text("old\n")
    files().lay_down(path, "new\n")
    assert path.read_text() == "new\n"


def test_pyproject_is_the_nearest_one_at_or_above_start_with_its_text(tmp_path):
    (tmp_path / "pyproject.toml").write_text("outer\n")
    (tmp_path / "inner").mkdir()
    (tmp_path / "inner" / "pyproject.toml").write_text("inner\n")
    (tmp_path / "inner" / "app").mkdir()
    assert files().pyproject(tmp_path / "inner" / "app") == (tmp_path / "inner" / "pyproject.toml", "inner\n")
    assert files().pyproject(tmp_path) == (tmp_path / "pyproject.toml", "outer\n")


def test_pyproject_is_none_when_there_is_none(tmp_path):
    start = tmp_path / "app"
    start.mkdir()
    assert files().pyproject(start) is None


def test_a_path_is_resolved_from_the_folder_given_with_its_links_followed_and_its_dots_taken(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real")
    assert (files().resolved(tmp_path / "real", Path("..") / "link"), files().resolved(tmp_path / "real", Path("."))) == (
        tmp_path / "real", tmp_path / "real")
