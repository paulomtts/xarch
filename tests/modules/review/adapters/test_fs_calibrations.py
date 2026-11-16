"""The record of the evals held to their examples on the filesystem: one JSON file, each eval by id with the hash of
what it was held as, the models, the verdict, the line, the value of each example by path (four decimals) and what
crossed, and no code and no question; an entry not of that shape is no record of it, and a file that cannot be read,
or is a link, is refused, naming it, and never rewritten."""
import json

import pytest

from xarch.modules.review.adapters.fs_calibrations import FsCalibrations
from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import DISAGREE, ELSEWHERE, PartHeld, PlacementHeld
from xarch.modules.review.domain.values import Calibration
from xarch.platform.data_files import DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

HELD = Calibration("ab" * 32, "jev-1.14.0", "jev-1.14.0.3", True, 0.55, (("services/a.py", 0.91234567),),
                   (("services/b.py", 0.1),), "")


def calibrations() -> FsCalibrations:
    return FsCalibrations(FileSystem(), DataFileReader(), DataFileWriter())


def test_the_evals_recorded_are_read_back_by_id_and_the_file_holds_no_code(tmp_path):
    record = tmp_path / ".xarch" / "calibration.json"
    calibrations().put(record, {"rule": HELD})
    assert calibrations().get(record) == {"rule": Calibration(HELD.held, HELD.model, HELD.answered, True, 0.55,
                                                              (("services/a.py", 0.9123),), (("services/b.py", 0.1),))}
    assert json.loads(record.read_text()) == {"evals": {"rule": {
        "hash": "ab" * 32, "model": "jev-1.14.0", "answered_by": "jev-1.14.0.3", "passed": True, "line": 0.55,
        "flagged": {"services/a.py": 0.9123}, "clean": {"services/b.py": 0.1}, "crossed": ""}}}


def test_no_file_is_no_record(tmp_path):
    assert calibrations().get(tmp_path / "calibration.json") == {}


@pytest.mark.parametrize("text", [
    pytest.param('{"evals": []}', id="evals that are not an object"),
    pytest.param('{"evals": {"rule": {"hash": "x", "model": "m", "answered_by": "m", "passed": "yes", "line": 0.5, '
                 '"flagged": {}, "clean": {}, "crossed": ""}}}', id="a verdict that is not true or false"),
    pytest.param('{"evals": {"rule": {"hash": "x", "model": "m", "answered_by": "m", "passed": true, "line": 0.5, '
                 '"flagged": {"a.py": 2}, "clean": {}, "crossed": ""}}}', id="a value above 1"),
    pytest.param('{"evals": {"rule": {"model": "m", "answered_by": "m", "passed": true, "line": 0.5, '
                 '"flagged": {}, "clean": {}, "crossed": ""}}}', id="no hash"),
])
def test_a_record_or_an_entry_not_of_the_shape_written_is_none(tmp_path, text):
    record = tmp_path / "calibration.json"
    record.write_text(text)
    assert calibrations().get(record) == {}


PLACED = PlacementHeld("cd" * 32, "jev-1.14.0", "jev-1.14.0.3", (PartHeld("domain", DISAGREE, "it crossed", 3),
                                                                PartHeld("kernel", ELSEWHERE)))


def test_placement_held_is_recorded_beside_the_evals_each_kept_when_the_other_is_written(tmp_path):
    record = tmp_path / ".xarch" / "calibration.json"
    calibrations().put(record, {"rule": HELD})
    calibrations().put_placement(record, PLACED)
    calibrations().put(record, {"rule": HELD})
    assert calibrations().placement(record) == PLACED and list(calibrations().get(record)) == ["rule"]
    assert json.loads(record.read_text())["placement"] == {
        "hash": "cd" * 32, "model": "jev-1.14.0", "answered_by": "jev-1.14.0.3",
        "parts": {"domain": {"verdict": "disagree", "crossed": "it crossed", "examples": 3},
                  "kernel": {"verdict": "elsewhere", "crossed": "", "examples": 0}}}


@pytest.mark.parametrize("text", [
    pytest.param('{"placement": []}', id="placement that is not an object"),
    pytest.param('{"placement": {"hash": "x", "model": "m", "answered_by": "m", "parts": {"a": {"verdict": 1, '
                 '"crossed": "", "examples": 0}}}}', id="a verdict that is not text"),
    pytest.param('{"placement": {"model": "m", "answered_by": "m", "parts": {}}}', id="no hash"),
])
def test_a_record_of_placement_not_of_the_shape_written_is_none(tmp_path, text):
    record = tmp_path / "calibration.json"
    record.write_text(text)
    assert calibrations().placement(record) is None and calibrations().placement(tmp_path / "none.json") is None


@pytest.mark.parametrize("use", [
    pytest.param(lambda held, record: held.get(record), id="reading the evals"),
    pytest.param(lambda held, record: held.placement(record), id="reading placement"),
    pytest.param(lambda held, record: held.put(record, {"rule": HELD}), id="writing the evals"),
    pytest.param(lambda held, record: held.put_placement(record, PlacementHeld("h", "m", "m", ())),
                 id="writing placement"),
])
@pytest.mark.parametrize("written, why", [
    pytest.param(b"<<<<<<< HEAD\n{}\n", "it is not JSON", id="a record a merge left its marks in"),
    pytest.param(b"[]", "it is not a JSON object", id="a document that is not an object"),
    pytest.param(b"\xff\xfe", "it is not UTF-8 text", id="a file that is not UTF-8"),
])
def test_a_record_that_cannot_be_read_is_refused_naming_it_and_never_rewritten(tmp_path, use, written, why):
    record = tmp_path / "calibration.json"
    record.write_bytes(written)
    with pytest.raises(Refused, match=f"the record {record} cannot be read \\({why}\\)"):
        use(calibrations(), record)
    assert record.read_bytes() == written


def test_a_record_that_is_a_link_is_neither_read_nor_written_through(tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("precious")
    record = tmp_path / "calibration.json"
    record.symlink_to(victim)
    for use in (lambda: calibrations().get(record), lambda: calibrations().put(record, {"rule": HELD})):
        with pytest.raises(Refused, match="is a link"):
            use()
    assert victim.read_text() == "precious"


def test_a_record_that_cannot_be_written_is_refused_naming_it(tmp_path):
    folder = tmp_path / "ro"
    folder.mkdir()
    folder.chmod(0o500)
    try:
        with pytest.raises(Refused, match=f"cannot write the record {folder / 'calibration.json'}"):
            calibrations().put(folder / "calibration.json", {"rule": HELD})
    finally:
        folder.chmod(0o700)
