"""Spec's Runtime port answered by the interpreter running xarch."""
from __future__ import annotations

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import LANGUAGES
from xarch.platform.interpreter import builtin_names, reserved_words, standard_library

SOURCE = "interpreter"
"""The one source of the standard library's names a language's data file may give."""


class InterpreterRuntime:
    """Satisfies spec's Runtime port."""

    def standard_library(self, source: str) -> frozenset[str]:
        _read(source)
        return standard_library()

    def reserved_words(self, source: str) -> frozenset[str]:
        _read(source)
        return reserved_words()

    def builtin_names(self, source: str) -> frozenset[str]:
        _read(source)
        return builtin_names()


def _read(source: str) -> None:
    """Refuses a source of names other than the interpreter, the one this runtime reads."""
    if source != SOURCE:
        raise InvalidArchitecture(LANGUAGES, [
            f"standard: {source!r} is not a source of names xarch reads: use {SOURCE}"])
