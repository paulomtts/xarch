"""Spec's Runtime port answered by the interpreter running xarch, for a language whose data file gives `standard:
interpreter`."""
from __future__ import annotations

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import INTERPRETER, LANGUAGES
from xarch.platform.interpreter import builtin_names, reserved_words, standard_library


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
    if source != INTERPRETER:
        raise InvalidArchitecture(LANGUAGES, [
            f"standard: {source!r} is not a source of names xarch reads: use {INTERPRETER}"])
