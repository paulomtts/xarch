"""The base error hierarchy. Each module subclasses it; `reason` is a message safe to show the caller."""
from __future__ import annotations


class DomainError(Exception):
    reason: str

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
