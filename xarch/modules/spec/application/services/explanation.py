from __future__ import annotations

from xarch.kernel.capabilities import FACTS
from xarch.modules.spec.application.logic.explain import (
    cleaned,
    example_of,
    held_by,
    key_at,
    nearest,
    overview_keys,
    said,
    supplied,
)
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import FormatExplained, KeyExplained, Need, Shown, Symbol, UnknownKey
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_LANGUAGES,
    CHOICE_PRESETS,
    SMALLEST,
    SYMBOLS,
    Key,
)
from xarch.modules.spec.domain.values import VERSION, Language


class ExplainService:
    """Explains the format of a profile in the words of the language an app is in when its profile names none, with
    the names xarch ships that a key may be set to."""

    def __init__(self, files: ArchitectureFiles, architectures: ArchitectureService):
        self._files, self._architectures = files, architectures

    def explain(self, address: str | None) -> FormatExplained | KeyExplained | UnknownKey:
        """The whole format with no address, else the key at it, or the nearest keys when the format has none there;
        raises InvalidArchitecture when the data file of a language does not load."""
        language = self._architectures.default_language()
        if address is None:
            shape = tuple(_shown(key, depth, language) for key, depth in overview_keys())
            return FormatExplained(VERSION, shape, tuple(Symbol(said(s, language), said(m, language)) for s, m in SYMBOLS),
                                   SMALLEST)
        key = key_at(address)
        if key is None:
            return UnknownKey(cleaned(address), nearest(cleaned(address)))
        names = self.choices(key)
        return KeyExplained(plain(key.address), key.where, said(key.meaning, language), said(key.accepts, language),
                            key.required, key.enforced, key.rules, said(example_of(key, names), language), names,
                            tuple(_shown(held, 0, language) for held in held_by(key)),
                            tuple(Need(fact, FACTS[fact], supplied(fact, language)) for fact in key.needs),
                            language.checked.title if key.needs else "",
                            bool(key.needs) and language.checked.supplies is not None)

    def choices(self, key: Key) -> tuple[str, ...]:
        """The bundled profiles, the `testing` presets or the languages, for a key that names one of them; else none."""
        if key.choices == CHOICE_BUNDLED:
            return self._files.bundled()
        if key.choices == CHOICE_LANGUAGES:
            return tuple(sorted(self._files.language_presets()))
        return tuple(self._files.testing_presets()) if key.choices == CHOICE_PRESETS else ()


def _shown(key: Key, depth: int, language: Language) -> Shown:
    return Shown(plain(key.address), depth, said(key.meaning, language), key.required, key.enforced)
