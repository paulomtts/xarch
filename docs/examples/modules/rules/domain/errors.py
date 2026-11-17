from __future__ import annotations

from app.kernel.errors import DomainError


class NoProfile(DomainError):
    pass


class ProfileUnusable(DomainError):
    pass


class SourceUnreadable(DomainError):
    def __init__(self, file: str, line: int, why: str):
        super().__init__(f"{file}:{line}: {why}")
        self.file, self.line = file, line
