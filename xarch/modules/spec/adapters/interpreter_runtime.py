"""Spec's Runtime port answered by the interpreter running xarch."""
from __future__ import annotations

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.platform.interpreter import builtin_names, reserved_words, standard_library

SOURCE = "interpreter"
"""The one source of the standard library's names a language's data file may give."""


class InterpreterRuntime:
    """Satisfies spec's Runtime port."""

    def standard_library(self, source: str) -> frozenset[str]:
        if source != SOURCE:
            raise InvalidArchitecture("presets/language", [
                f"standard: {source!r} is not a source of names xarch reads: use {SOURCE}"])
        return standard_library()

    def reserved_words(self) -> frozenset[str]:
        return reserved_words()

    def builtin_names(self) -> frozenset[str]:
        return builtin_names()
