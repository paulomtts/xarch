from __future__ import annotations

from xarch.modules.spec.application.logic.explain import (
    DEEPER,
    VERSION,
    cleaned,
    example_of,
    held_by,
    key_at,
    nearest,
    overview_keys,
)
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.contract import Explain, ExplainResult, FormatExplained, KeyExplained, Shown, Symbol, UnknownKey
from xarch.modules.spec.domain.profile_keys import CHOICE_BUNDLED, CHOICE_PRESETS, SMALLEST, SYMBOLS, Key, plain


class ExplainService:
    """Explains the format of a profile from the table of keys, with the names xarch ships that a key may be set to."""

    def __init__(self, files: ArchitectureFiles):
        self._files = files

    def explain(self, cmd: Explain) -> ExplainResult:
        if cmd.key is None:
            shape = tuple(_shown(key, depth) for key, depth in overview_keys())
            return FormatExplained(VERSION, shape, tuple(Symbol(s, m) for s, m in SYMBOLS), SMALLEST, DEEPER)
        key = key_at(cmd.key)
        if key is None:
            return UnknownKey(cleaned(cmd.key), nearest(cleaned(cmd.key)))
        names = self._choices(key)
        return KeyExplained(plain(key.address), key.where, key.meaning, key.accepts, key.required, key.enforced,
                            key.rules, example_of(key, names), names, tuple(_shown(held, 0) for held in held_by(key)))

    def _choices(self, key: Key) -> tuple[str, ...]:
        if key.choices == CHOICE_BUNDLED:
            return self._files.bundled()
        return tuple(self._files.testing_presets()) if key.choices == CHOICE_PRESETS else ()


def _shown(key: Key, depth: int) -> Shown:
    return Shown(plain(key.address), depth, key.meaning, key.required, key.enforced)
