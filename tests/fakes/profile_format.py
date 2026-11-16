"""In-memory implementation of spec's ProfileFormat port. Not an adapter: a test double only."""
from __future__ import annotations

from typing import Any


class FakeProfileFormat:
    """Satisfies spec's ProfileFormat: each top-level key on a line of its own, `key: value`, the value as Python
    shows it; renamed, the lines but `based_on` as they are, and `based_on` after the `name` line, which says the new
    name."""

    def written(self, document: dict[str, Any]) -> bytes:
        return "".join(f"{key}: {value}\n" for key, value in document.items()).encode("utf-8")

    def renamed(self, text: str, name: str, based_on: str) -> str | None:
        lines = [line for line in text.splitlines(keepends=True) if not line.startswith("based_on:")]
        named = [i for i, line in enumerate(lines) if line.startswith("name:")]
        if not named:
            return None
        lines[named[0]] = f"name: {name}\nbased_on: {based_on}\n"
        return "".join(lines)
