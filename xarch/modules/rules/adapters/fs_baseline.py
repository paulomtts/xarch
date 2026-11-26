"""The record of the baseline, one JSON file in the project beside the other records xarch keeps, .xarch/baseline.json:
a version, then each finding recorded with its rule, file, message and count, in the order of rule, file and message,
two spaces to a level, so that a diff of it reads in review."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.published import Recorded
from xarch.platform.data_files import DataFileError, DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

VERSION = 1
"""The version of the record's shape read and written here."""
FIELDS = ("rule", "file", "message", "count")
"""The fields of each finding recorded, in the order written."""


class FsBaselines:
    """Satisfies rules' Baselines port on the filesystem."""

    def __init__(self, fs: FileSystem, reader: DataFileReader, writer: DataFileWriter):
        self._fs, self._reader, self._writer = fs, reader, writer

    def read(self, record: Path) -> tuple[Recorded, ...] | None:
        """None when there is no record; one that cannot be read raises ProfileUnusable with why."""
        if not self._fs.exists(record):
            return None
        try:
            document = self._reader.parse(self._fs.read_text(record), json_syntax=True)
        except (DataFileError, OSError, UnicodeDecodeError):
            document = None
        found = _findings(document)
        if found is None:
            raise ProfileUnusable(f"the baseline {record} cannot be read: it is no JSON {{\"version\": {VERSION}, "
                                  "\"findings\": [{rule, file, message, count}, ...]}: mend it, or write it again with "
                                  "`xarch baseline write --reset`")
        return found

    def write(self, record: Path, findings: tuple[Recorded, ...]) -> None:
        """Raises ProfileUnusable with why when the record cannot be written."""
        document = {"version": VERSION, "findings": [dict(zip(FIELDS, (f.rule, f.file, f.message, f.count), strict=True))
                                                     for f in findings]}
        try:
            self._fs.write_text(record, self._writer.json(document))
        except OSError as e:
            raise ProfileUnusable(f"cannot write the baseline {record}: {e.strerror or type(e).__name__}") from None


def _findings(document: Any) -> tuple[Recorded, ...] | None:
    """The findings a document of the record holds; None when it is no record of VERSION."""
    if not isinstance(document, dict) or document.get("version") != VERSION:
        return None
    listed = document.get("findings")
    if not isinstance(listed, list):
        return None
    found: list[Recorded] = []
    for entry in listed:
        if not isinstance(entry, dict):
            return None
        rule, file, message, count = (entry.get(key) for key in FIELDS)
        if not (isinstance(rule, str) and isinstance(file, str) and isinstance(message, str)):
            return None
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            return None
        found.append(Recorded(rule, file, message, count))
    return tuple(found)
