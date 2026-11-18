"""The record of the doubtful files accepted on the filesystem: one JSON file, each file by its path as review shows it
with the part it lay in, the part it read as, the hash of its code and why, in the order of the paths and two spaces to
a level; an entry not of that shape is no record of it, and a file that cannot be read, or is a link, is refused,
naming it, and never rewritten."""
import json

import pytest

from xarch.modules.review.adapters.fs_acceptances import FsAcceptances
from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import AcceptedFile
from xarch.platform.data_files import DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

ONE = AcceptedFile("logic", "profile-values", "ab" * 32, "it decides one rule over the profile's documents")
TWO = AcceptedFile("domain", "logic", "cd" * 32, "an error the module raises")


def acceptances() -> FsAcceptances:
    return FsAcceptances(FileSystem(), DataFileReader(), DataFileWriter())


def test_the_files_accepted_are_read_back_by_file_and_written_in_the_order_of_their_paths(tmp_path):
    record = tmp_path / ".xarch" / "accepted.json"
    acceptances().put(record, {"app/z.py": ONE, "app/a.py": TWO})
    assert acceptances().get(record) == {"app/a.py": TWO, "app/z.py": ONE}
    text = record.read_text()
    assert list(json.loads(text)) == ["app/a.py", "app/z.py"]
    assert json.loads(text)["app/z.py"] == {"part": "logic", "reads_as": "profile-values", "hash": "ab" * 32,
                                           "why": "it decides one rule over the profile's documents"}
    assert text.startswith('{\n  "app/a.py": {\n    "part": "domain",') and text.endswith("}\n")


def test_no_file_is_no_record(tmp_path):
    assert acceptances().get(tmp_path / "accepted.json") == {}


@pytest.mark.parametrize("text", [
    pytest.param('{"app/a.py": []}', id="an entry that is not an object"),
    pytest.param('{"app/a.py": {"part": "logic", "reads_as": "domain", "why": "w"}}', id="no hash"),
    pytest.param('{"app/a.py": {"part": "logic", "reads_as": "domain", "hash": 3, "why": "w"}}', id="a hash not text"),
])
def test_an_entry_not_of_the_shape_written_is_none(tmp_path, text):
    record = tmp_path / "accepted.json"
    record.write_text(text)
    assert acceptances().get(record) == {}


@pytest.mark.parametrize("text", [pytest.param("<<<<<<< HEAD\n", id="not JSON"), pytest.param("[]", id="no object")])
def test_a_record_that_cannot_be_read_is_refused_naming_it_and_never_rewritten(tmp_path, text):
    record = tmp_path / "accepted.json"
    record.write_text(text)
    with pytest.raises(Refused, match=f"the record of accepted files {record} cannot be read"):
        acceptances().get(record)
    with pytest.raises(Refused, match="cannot be read"):
        acceptances().put(record, {"app/a.py": ONE})
    assert record.read_text() == text


def test_a_record_that_is_a_link_is_refused_and_never_written_through(tmp_path):
    target = tmp_path / "elsewhere.json"
    target.write_text("{}")
    record = tmp_path / "accepted.json"
    record.symlink_to(target)
    with pytest.raises(Refused, match="is a link"):
        acceptances().get(record)
    with pytest.raises(Refused, match="is a link"):
        acceptances().put(record, {"app/a.py": ONE})
    assert target.read_text() == "{}"


def test_a_record_that_cannot_be_written_is_refused_naming_it(tmp_path):
    (tmp_path / "file").write_text("")
    with pytest.raises(Refused, match="cannot write the record of accepted files"):
        acceptances().put(tmp_path / "file" / "accepted.json", {"app/a.py": ONE})
