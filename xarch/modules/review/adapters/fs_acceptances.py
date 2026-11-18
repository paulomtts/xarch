"""The record of the doubtful files a person accepted, one JSON file in the project beside the record of the evals,
which the project commits: for each file, by its path as review shows it, the part it lay in, the part it read as, the
hash of its code and why it was accepted, the files in the order of their paths, two spaces to a level, so that a diff
of it reads; no code, no absolute path, no key."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import AcceptedFile
from xarch.platform.data_files import DataFileError, DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

FIELDS = ("part", "reads_as", "hash", "why")
"""The fields of each file recorded, in the order written."""


class FsAcceptances:
    """Satisfies review's Acceptances on the filesystem."""

    def __init__(self, fs: FileSystem, reader: DataFileReader, writer: DataFileWriter):
        self._fs, self._reader, self._writer = fs, reader, writer

    def get(self, record: Path) -> dict[str, AcceptedFile]:
        """An entry not of the shape written is left out."""
        return {str(file): found for file, entry in self._read(record).items() if (found := _accepted(entry))}

    def put(self, record: Path, accepted: dict[str, AcceptedFile]) -> None:
        self._read(record)
        written = {file: dict(zip(FIELDS, (entry.part, entry.reads_as, entry.code, entry.why), strict=True))
                   for file, entry in sorted(accepted.items())}
        try:
            self._fs.write_text(record, self._writer.json(written))
        except OSError as e:
            raise Refused(f"cannot write the record of accepted files {record}: "
                          f"{e.strerror or type(e).__name__}") from None

    def _read(self, record: Path) -> dict[str, Any]:
        """The record as written, empty when there is none; one that is a link or cannot be read raises Refused,
        naming it, and is never rewritten."""
        if self._fs.is_link(record):
            raise Refused(f"the record of accepted files {record} is a link: review reads and writes no record through "
                          "a link")
        if not self._fs.exists(record):
            return {}
        try:
            kept = self._reader.parse(self._fs.read_text(record), json_syntax=True)
        except (DataFileError, OSError, UnicodeDecodeError):
            kept = None
        if not isinstance(kept, dict):
            raise Refused(f"the record of accepted files {record} cannot be read (it is no JSON object of UTF-8 text): "
                          "mend it, or remove it to accept the files again; it is not rewritten while it cannot be "
                          "read")
        return kept


def _accepted(entry: Any) -> AcceptedFile | None:
    if not isinstance(entry, dict) or not all(isinstance(entry.get(name), str) for name in FIELDS):
        return None
    return AcceptedFile(entry["part"], entry["reads_as"], entry["hash"], entry["why"])
