"""Spec's ProfileOutput on the real filesystem: which files of a folder are taken already, and writing every file of a
profile with the folders above it."""
from xarch.modules.spec.adapters.fs_profile_output import FsProfileOutput
from xarch.platform.filesystem import FileSystem


def test_the_files_taken_in_a_folder_are_named_in_the_order_given(tmp_path):
    (tmp_path / "out" / "docs").mkdir(parents=True)
    (tmp_path / "out" / "mine.yaml").write_text("")
    output = FsProfileOutput(FileSystem())
    assert output.taken(tmp_path / "out", ["docs", "new.md", "mine.yaml"]) == [tmp_path / "out" / "docs",
                                                                               tmp_path / "out" / "mine.yaml"]


def test_every_file_is_written_at_its_path_in_the_folder(tmp_path):
    FsProfileOutput(FileSystem()).write(tmp_path / "out", {"mine.yaml": b"name: mine\n", "docs/a.md": b"page\n"})
    assert (tmp_path / "out" / "mine.yaml").read_bytes() == b"name: mine\n"
    assert (tmp_path / "out" / "docs" / "a.md").read_bytes() == b"page\n"
