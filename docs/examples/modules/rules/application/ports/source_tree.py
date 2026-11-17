from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.kernel.source import Import


class SourceTree(Protocol):
    def files(self, root: Path, extension: str) -> list[str]:
        ...

    def imports(self, root: Path, file: str) -> tuple[Import, ...]:
        ...
