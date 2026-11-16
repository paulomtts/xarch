"""The record of the evals of the profile's own held to their examples, one JSON file in the project, which the
project commits: for each eval by id, the hash of what it was held as, the model asked and the version that answered,
the verdict, the line, the value of each example file by path and what crossed; no code and no question."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import PartHeld, PlacementHeld
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
        """An entry not of the shape written is left out."""
        evals = self._document(record).get("evals")
        if not isinstance(evals, dict):
            return {}
        return {str(name): found for name, entry in evals.items() if (found := _held(entry)) is not None}

    def put(self, record: Path, held: dict[str, Calibration]) -> None:
        document = self._document(record)
        document["evals"] = {name: _entry(entry) for name, entry in sorted(held.items())}
        self._write(record, document)

    def placement(self, record: Path) -> PlacementHeld | None:
        """A record of placement not of the shape written is none."""
        return _placed(self._document(record).get("placement"))

    def put_placement(self, record: Path, held: PlacementHeld) -> None:
        document = self._document(record)
        document["placement"] = {"hash": held.held, "model": held.model, "answered_by": held.answered,
                                 "parts": {part.part: {"verdict": part.verdict, "crossed": part.crossed,
                                                       "examples": part.examples} for part in held.parts}}
        self._write(record, document)

    def _write(self, record: Path, document: dict[str, Any]) -> None:
        try:
            self._fs.write_text(record, self._writer.json(dict(sorted(document.items()))))
        except OSError as e:
            raise Refused(f"cannot write the record {record}: {e.strerror or type(e).__name__}") from None

    def _document(self, record: Path) -> dict[str, Any]:
        """The record as written; empty when there is none. A link, or a record that cannot be read, raises Refused
        naming it, and is never rewritten."""
        if self._fs.is_link(record):
            raise Refused(f"the record {record} is a link: review reads and writes no record through a link")
        if not self._fs.exists(record):
            return {}
        try:
            kept = self._reader.parse(self._fs.read_text(record), json_syntax=True)
        except (DataFileError, OSError, UnicodeDecodeError) as e:
            raise Refused(f"the record {record} cannot be read ({_why(e)}): mend it, or remove it to hold every eval "
                          "again; it is not rewritten while it cannot be read") from None
        if not isinstance(kept, dict):
            raise Refused(f"the record {record} cannot be read (it is not a JSON object): mend it, or remove it to "
                          "hold every eval again; it is not rewritten while it cannot be read")
        return kept


def _why(error: Exception) -> str:
    """Why a record cannot be read, in a few words."""
    if isinstance(error, UnicodeDecodeError):
        return "it is not UTF-8 text"
    if isinstance(error, OSError):
        return error.strerror or type(error).__name__
    return "it is not JSON"


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


def _placed(entry: Any) -> PlacementHeld | None:
    if not isinstance(entry, dict) or not isinstance(entry.get("parts"), dict):
        return None
    texts = [entry.get(key) for key in ("hash", "model", "answered_by")]
    parts = [(name, held) for name, held in entry["parts"].items() if isinstance(held, dict)]
    if not all(isinstance(text, str) for text in texts) or len(parts) != len(entry["parts"]):
        return None
    if not all(isinstance(held.get("verdict"), str) and isinstance(held.get("crossed"), str)
               and isinstance(held.get("examples"), int) for _, held in parts):
        return None
    return PlacementHeld(texts[0], texts[1], texts[2], tuple(PartHeld(str(name), held["verdict"], held["crossed"],
                                                                      held["examples"]) for name, held in parts))
