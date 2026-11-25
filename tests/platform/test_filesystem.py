"""The local filesystem in plain paths: what is there, the files and folders below a folder, the nearest file of a name
above a folder, and writing that makes the folders above."""
from pathlib import Path

import pytest

from xarch.platform.filesystem import FileSystem


def tree(root):
    (root / "a" / "b").mkdir(parents=True)
    (root / "a" / "x.py").write_text("x")
    (root / "a" / "b" / "y.txt").write_text("y")
    (root / "top.py").write_text("")
    return root


def test_what_is_at_a_path(tmp_path):
    fs = FileSystem()
    tree(tmp_path)
    assert [fs.exists(tmp_path / "a"), fs.is_dir(tmp_path / "a"), fs.is_file(tmp_path / "a")] == [True, True, False]
    assert [fs.exists(tmp_path / "gone"), fs.is_file(tmp_path / "top.py")] == [False, True]


def test_the_folders_and_files_below_a_folder_are_listed_sorted_and_none_below_what_is_no_folder(tmp_path):
    fs = FileSystem()
    tree(tmp_path)
    assert fs.subdirectories(tmp_path) == ["a"]
    assert fs.folders(tmp_path) == [("a",), ("a", "b")]
    assert fs.files_below(tmp_path / "a") == ["b/y.txt", "x.py"]
    assert fs.files(tmp_path, "*.py") == [tmp_path / "a" / "x.py", tmp_path / "top.py"]
    assert (fs.subdirectories(tmp_path / "top.py"), fs.folders(tmp_path / "gone"), fs.files_below(tmp_path / "gone")) == (
        [], [], [])


def test_a_folder_the_filesystem_hides_is_not_listed_nor_any_inside_it_by_either_listing(tmp_path):
    (tree(tmp_path) / ".cache" / "c").mkdir(parents=True)
    (tmp_path / "a" / ".git").mkdir()
    assert FileSystem().folders(tmp_path) == [("a",), ("a", "b")]
    assert FileSystem().subdirectories(tmp_path) == ["a"]


def test_the_nearest_file_of_a_name_is_found_in_the_folder_or_above_it(tmp_path):
    fs = FileSystem()
    tree(tmp_path)
    (tmp_path / "a" / "pyproject.toml").write_text("")
    assert fs.find_upward(tmp_path / "a" / "b", "pyproject.toml") == tmp_path / "a" / "pyproject.toml"
    assert fs.find_upward(tmp_path / "a" / "b", "nothing.here") is None


def test_a_relative_start_is_refused_by_the_upward_search():
    with pytest.raises(ValueError, match="is not a path in full"):
        FileSystem().find_upward(Path("a"), "pyproject.toml")


def test_writing_makes_the_folders_above_and_reads_back(tmp_path):
    fs = FileSystem()
    fs.write_text(tmp_path / "new" / "deep" / "a.txt", "text")
    fs.write_bytes(tmp_path / "new" / "b.bin", b"\x00\x01")
    fs.create_empty(tmp_path / "c" / "e.py")
    assert fs.read_text(tmp_path / "new" / "deep" / "a.txt") == "text"
    assert fs.read_bytes(tmp_path / "new" / "b.bin") == b"\x00\x01"
    assert fs.read_text(tmp_path / "c" / "e.py") == ""


def test_a_path_in_full_is_read_with_its_links_followed_and_its_dots_taken(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real")
    assert FileSystem().real(tmp_path / "real" / ".." / "link") == tmp_path / "real"


def test_a_relative_path_is_refused_since_its_caller_says_which_folder_it_is_read_from():
    with pytest.raises(ValueError, match="is not a path in full"):
        FileSystem().real(Path("link"))


def test_a_link_is_known_as_one_and_removing_it_leaves_what_it_points_to(tmp_path):
    fs = FileSystem()
    (tmp_path / "kept.txt").write_text("precious")
    (tmp_path / "link.txt").symlink_to(tmp_path / "kept.txt")
    (tmp_path / "dangling").symlink_to(tmp_path / "gone")
    assert [fs.is_link(tmp_path / name) for name in ("link.txt", "dangling", "kept.txt", "absent")] == [
        True, True, False, False]
    fs.remove(tmp_path / "link.txt")
    fs.remove(tmp_path / "absent")
    assert not (tmp_path / "link.txt").exists() and (tmp_path / "kept.txt").read_text() == "precious"


def test_bytes_replaced_whole_land_in_the_folders_made_above_and_leave_nothing_beside_them(tmp_path):
    fs = FileSystem()
    target = tmp_path / "new" / "deep" / "kept.bin"
    fs.replace_bytes(target, b"first")
    fs.replace_bytes(target, b"second")
    assert fs.read_bytes(target) == b"second"
    assert sorted(p.name for p in target.parent.iterdir()) == ["kept.bin"]


def test_bytes_that_cannot_be_written_raise_and_leave_nothing_behind(tmp_path):
    (tmp_path / "taken").write_text("a file, not a folder\n")
    with pytest.raises(FileExistsError):
        FileSystem().replace_bytes(tmp_path / "taken" / "kept.bin", b"data")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["taken"]
