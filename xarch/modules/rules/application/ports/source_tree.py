from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.values import SourceFile


class SourceTree(Protocol):
    """The Python files below a root folder, with their imports already parsed."""

    def is_dir(self, root: Path) -> bool: ...

    def read(self, root: Path) -> list[SourceFile]: ...
