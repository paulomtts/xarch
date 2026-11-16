"""The record of the evals held to their examples on the filesystem: one JSON file, each eval by id with the hash of
what it was held as, the models, the verdict, the line, the value of each example by path (four decimals) and what
crossed, and no code and no question; a file or an entry not of that shape is no record of it."""
import json

import pytest

from xarch.modules.review.adapters.fs_calibrations import FsCalibrations
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
    pytest.param("not json", id="a file that is not JSON"),
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
