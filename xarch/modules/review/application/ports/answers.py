from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import Answer


class Answers(Protocol):
    """The answers kept in a folder, each under its key, holding no text of the code and no question."""

    def get(self, folder: Path, key: str) -> Answer | None:
        """The answer kept under the key; None when there is none, or none that can be read."""
        ...

    def put(self, folder: Path, key: str, answer: Answer) -> None:
        """Keep the answer under the key, creating the folder."""
        ...
