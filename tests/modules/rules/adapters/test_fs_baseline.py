"""The baseline recorded on disk: written as JSON two spaces to a level and read back the same; no file is no record,
and a file that is no record of the version written is refused with why."""
import json

import pytest

from xarch.modules.rules.adapters.fs_baseline import FsBaselines
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.published import Recorded
from xarch.platform.data_files import DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

FOUND = (Recorded("may-import", "app/a.py", "a/ may not import b/", 2), Recorded("structure", "app", "missing x/", 1))


def baselines() -> FsBaselines:
    return FsBaselines(FileSystem(), DataFileReader(), DataFileWriter())


def test_a_record_written_reads_back_the_same(tmp_path):
    record = tmp_path / ".xarch" / "baseline.json"
    baselines().write(record, FOUND)
    assert baselines().read(record) == FOUND
    assert json.loads(record.read_text())["findings"][0] == {"rule": "may-import", "file": "app/a.py",
                                                             "message": "a/ may not import b/", "count": 2}
    assert record.read_text().startswith('{\n  "version": 1,')


def test_no_file_is_no_record(tmp_path):
    assert baselines().read(tmp_path / "baseline.json") is None


@pytest.mark.parametrize("text", ["{", "[]", '{"version": 2, "findings": []}', '{"version": 1, "findings": [{}]}',
                                  '{"version": 1, "findings": [{"rule": "r", "file": "f", "message": "m", "count": 0}]}'])
def test_a_file_that_is_no_record_is_refused(tmp_path, text):
    record = tmp_path / "baseline.json"
    record.write_text(text)
    with pytest.raises(ProfileUnusable, match="cannot be read"):
        baselines().read(record)
