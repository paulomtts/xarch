from __future__ import annotations

from typing import Protocol


class Runtime(Protocol):
    """What only the runtime of the language knows: names that no data file could keep current."""

    def standard_library(self, source: str) -> frozenset[str]:
        """The top-level names of the standard library, known from source, a name a language's data file gives; raises
        InvalidArchitecture for a source it does not read."""
        ...

    def reserved_words(self) -> frozenset[str]:
        """The words no name may be."""
        ...

    def builtin_names(self) -> frozenset[str]:
        """The names the language binds without an import."""
        ...
