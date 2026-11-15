"""Layout's Disk on the real filesystem: which required folders and files exist, which folders a repeating folder
holds, and which lie below it."""
from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.modules.layout.domain.structure import Requirement
from xarch.platform.filesystem import FileSystem


def test_the_disk_says_which_required_folders_and_files_exist_as_the_kind_they_must_be(tmp_path):
    (tmp_path / "modules").mkdir()
    (tmp_path / "__main__.py").write_text("")
    folder = Requirement("app", ("modules",), True, "modules/")
    file = Requirement("app", ("__main__.py",), False, "__main__.py")
    folder_as_file = Requirement("app", ("modules",), False, "modules")
    file_as_folder = Requirement("app", ("__main__.py",), True, "__main__.py/")
    gone = Requirement("app", ("gone",), True, "gone/")
    required = [folder, file, folder_as_file, file_as_folder, gone]
    assert FsDisk(FileSystem()).present(tmp_path, required) == {folder, file}


def test_the_disk_lists_the_instances_and_the_folders_of_a_repeating_folder(tmp_path):
    (tmp_path / "modules" / "docs" / "domain").mkdir(parents=True)
    disk = FsDisk(FileSystem())
    assert disk.instances(tmp_path, ("modules",)) == ["docs"]
    assert disk.below(tmp_path, ("modules",)) == [("docs",), ("docs", "domain")]
    assert (disk.instances(tmp_path, ("plugins",)), disk.below(tmp_path, ("plugins",))) == ([], [])
