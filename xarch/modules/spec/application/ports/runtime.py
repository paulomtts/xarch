from __future__ import annotations

from typing import Protocol


class Runtime(Protocol):
    """What only the runtime of a language knows: names that no data file could keep current. Each is known from
    source, the name a language's data file gives as its `standard`, so that each language gets its own; each raises
    InvalidArchitecture for a source it does not read."""

    def standard_library(self, source: str) -> frozenset[str]:
        """The top-level names of the standard library."""
        ...

    def reserved_words(self, source: str) -> frozenset[str]:
        """The words no name may be."""
        ...

    def builtin_names(self, source: str) -> frozenset[str]:
        """The names the language binds without an import."""
        ...
