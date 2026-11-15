"""In-memory implementation of spec's ExampleReader port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.kernel.logic.source import Import, Unparsable


class FakeExampleReader:
    """Satisfies spec's ExampleReader: what each text given imports, or where it does not parse; any other text imports
    nothing."""

    def __init__(self, reads: dict[str, tuple[Import, ...] | Unparsable] | None = None):
        self._reads = dict(reads or {})

    def imports(self, text: str) -> tuple[Import, ...] | Unparsable:
        return self._reads.get(text, ())
