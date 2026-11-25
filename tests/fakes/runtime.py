"""In-memory implementation of spec's Runtime port. Not an adapter: a test double only."""
from __future__ import annotations


class FakeRuntime:
    """Satisfies spec's Runtime: the standard library, the builtins and the reserved words as given, whatever the
    source; it records each source it is asked about, in order (asked)."""

    def __init__(self, standard: frozenset[str] = frozenset(), builtins: frozenset[str] = frozenset(),
                 reserved: frozenset[str] = frozenset()):
        self._standard, self._builtins, self._reserved = standard, builtins, reserved
        self.asked: list[str] = []

    def standard_library(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._standard

    def reserved_words(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._reserved

    def builtin_names(self, source: str) -> frozenset[str]:
        self.asked.append(source)
        return self._builtins
