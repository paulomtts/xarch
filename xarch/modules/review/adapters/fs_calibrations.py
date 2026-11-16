"""The record of the evals of the profile's own held to their examples, one JSON file in the project, which the
project commits: for each eval by id, the hash of what it was held as, the model asked and the version that answered,
the verdict, the line, the value of each example file by path and what crossed; no code and no question."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.review.domain.values import Calibration
from xarch.platform.data_files import DataFileError, DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

DIGITS = 4
"""How many decimals a value of an example keeps in the record: enough to compare, few enough to read in a diff."""


class FsCalibrations:
    """Satisfies review's Calibrations on the filesystem."""

    def __init__(self, fs: FileSystem, reader: DataFileReader, writer: DataFileWriter):
        self._fs, self._reader, self._writer = fs, reader, writer

    def get(self, record: Path) -> dict[str, Calibration]:
        """A file that cannot be read is no record; an entry not of the shape written is left out."""
        if not self._fs.is_file(record):
            return {}
        try:
            kept = self._reader.parse(self._fs.read_text(record), json_syntax=True)
        except (DataFileError, OSError, UnicodeDecodeError):
            return {}
        evals = kept.get("evals") if isinstance(kept, dict) else None
        if not isinstance(evals, dict):
            return {}
        return {str(name): found for name, entry in evals.items() if (found := _held(entry)) is not None}

    def put(self, record: Path, held: dict[str, Calibration]) -> None:
        self._fs.write_text(record, self._writer.json({"evals": {name: _entry(entry)
                                                                for name, entry in sorted(held.items())}}))


def _entry(entry: Calibration) -> dict[str, Any]:
    return {"hash": entry.held, "model": entry.model, "answered_by": entry.answered, "passed": entry.passed,
            "line": entry.line, "flagged": {path: round(found, DIGITS) for path, found in entry.flagged},
            "clean": {path: round(found, DIGITS) for path, found in entry.clean}, "crossed": entry.crossed}


def _held(entry: Any) -> Calibration | None:
    if not isinstance(entry, dict):
        return None
    texts = [entry.get(key) for key in ("hash", "model", "answered_by", "crossed")]
    passed, line = entry.get("passed"), entry.get("line")
    values = [entry.get(key) for key in ("flagged", "clean")]
    if not all(isinstance(text, str) for text in texts) or not isinstance(passed, bool) or not _number(line):
        return None
    if not all(isinstance(found, dict) and all(_number(v) for v in found.values()) for found in values):
        return None
    flagged, clean = (tuple((str(path), float(v)) for path, v in found.items()) for found in values)
    return Calibration(texts[0], texts[1], texts[2], passed, float(line), flagged, clean, texts[3])


def _number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and 0 <= value <= 1
