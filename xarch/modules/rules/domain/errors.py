from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError


class RootMissing(DomainError):
    def __init__(self, root: Path):
        super().__init__(f"{root} is not a directory")
        self.root = root
