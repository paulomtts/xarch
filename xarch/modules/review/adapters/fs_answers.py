"""The answers review keeps, one JSON file per question in a folder of the project, which the project commits: each
holds the model version that answered, the probability of each option and the tokens spent, and no text of the code,
no question and no key."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.review.domain.values import Answer
from xarch.platform.data_files import DataFileError, DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

ENDING = ".json"
"""The ending of the name of a file that keeps an answer, after its key."""


class FsAnswers:
    """Satisfies review's Answers on the filesystem."""

    def __init__(self, fs: FileSystem, reader: DataFileReader, writer: DataFileWriter):
        self._fs, self._reader, self._writer = fs, reader, writer

    def get(self, folder: Path, key: str) -> Answer | None:
        """A file that cannot be read, or holds no answer of the shape written, is no answer."""
        path = folder / f"{key}{ENDING}"
        if not self._fs.is_file(path):
            return None
        try:
            kept = self._reader.parse(self._fs.read_text(path), json_syntax=True)
        except (DataFileError, OSError, UnicodeDecodeError):
            return None
        return _answer(kept)

    def put(self, folder: Path, key: str, answer: Answer) -> None:
        self._fs.write_text(folder / f"{key}{ENDING}", self._writer.json({
            "model": answer.model, "probabilities": dict(answer.probabilities),
            "input_tokens": answer.input_tokens, "output_tokens": answer.output_tokens}))


def _answer(kept: Any) -> Answer | None:
    if not isinstance(kept, dict) or not isinstance(kept.get("model"), str):
        return None
    probabilities, spent = kept.get("probabilities"), (kept.get("input_tokens"), kept.get("output_tokens"))
    if not isinstance(probabilities, dict) or not all(_number(value) for value in probabilities.values()):
        return None
    if not all(isinstance(count, int) and not isinstance(count, bool) for count in spent):
        return None
    return Answer(kept["model"], tuple((str(name), float(value)) for name, value in probabilities.items()), *spent)


def _number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and 0 <= value <= 1
