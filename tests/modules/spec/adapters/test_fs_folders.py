"""Spec's Folders on the real filesystem: which of the paths asked about are folders."""
from xarch.modules.spec.adapters.fs_folders import FsFolders
from xarch.platform.filesystem import FileSystem


def test_only_the_paths_that_are_folders_come_back_in_the_order_given(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "file.py").write_text("")
    asked = [tmp_path / "gone", tmp_path / "tests", tmp_path / "file.py"]
    assert FsFolders(FileSystem()).existing(asked) == (tmp_path / "tests",)


def test_the_working_folder_is_the_one_the_process_works_in(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert FsFolders(FileSystem()).working_folder() == tmp_path.resolve()
