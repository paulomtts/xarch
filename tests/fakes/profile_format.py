"""In-memory implementation of spec's ProfileFormat port. Not an adapter: a test double only."""
from __future__ import annotations

from typing import Any


class FakeProfileFormat:
    """Satisfies spec's ProfileFormat: each top-level key on a line of its own, `key: value`, the value as Python
    shows it."""

    def written(self, document: dict[str, Any]) -> bytes:
        return "".join(f"{key}: {value}\n" for key, value in document.items()).encode("utf-8")
