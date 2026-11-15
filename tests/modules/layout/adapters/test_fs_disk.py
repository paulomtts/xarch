"""Layout's Disk on the real filesystem: what is a folder or a file below the root, and which folders lie below one."""
from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.platform.filesystem import FileSystem


def test_the_disk_says_what_is_a_folder_or_a_file_and_lists_the_folders_below_one(tmp_path):
    (tmp_path / "modules" / "docs" / "domain").mkdir(parents=True)
    (tmp_path / "__main__.py").write_text("")
    disk = FsDisk(FileSystem())
    assert [disk.is_dir(tmp_path / "modules"), disk.is_file(tmp_path / "modules")] == [True, False]
    assert [disk.is_file(tmp_path / "__main__.py"), disk.is_dir(tmp_path / "gone")] == [True, False]
    assert disk.subdirectories(tmp_path / "modules") == ["docs"]
    assert disk.folders(tmp_path / "modules") == [("docs",), ("docs", "domain")]
