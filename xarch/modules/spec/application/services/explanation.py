from __future__ import annotations

from xarch.modules.spec.application.logic.explain import (
    cleaned,
    example_of,
    graded,
    graded_for,
    held_by,
    holder_of,
    key_at,
    nearest,
    overview_keys,
    said,
    short,
    supplied,
)
from xarch.modules.spec.application.logic.key_catalogue import catalogue_of
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import FormatExplained, KeyExplained, Need, Shown, Symbol, UnknownKey
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_LANGUAGES,
    CHOICE_PRESETS,
    Catalogue,
    Key,
)
from xarch.modules.spec.domain.values import VERSION, Language
from xarch.profile_values.capabilities import FACTS


class ExplainService:
    """Explains the format of a profile in the words of the language an app is in when its profile names none, with
    the names xarch ships that a key may be set to."""

    def __init__(self, files: ArchitectureFiles, architectures: ArchitectureService):
        self._files, self._architectures = files, architectures
        self._catalogue: Catalogue | None = None

    def explain(self, address: str | None) -> FormatExplained | KeyExplained | UnknownKey:
        """The whole format with no address, else the key at it, or the nearest keys when the format has none there;
        raises InvalidArchitecture when the data file of a language, or of the format's texts, does not load."""
        language = self._architectures.default_language()
        catalogue = self._texts()
        if address is None:
            shape = tuple(_shown(key, depth, catalogue, language) for key, depth in overview_keys())
            return FormatExplained(VERSION, shape, tuple(Symbol(said(s, language), said(m, language))
                                                         for s, m in catalogue.symbols), catalogue.smallest)
        key = key_at(address)
        if key is None:
            return UnknownKey(cleaned(address), nearest(cleaned(address)))
        names, text = self.choices(key), catalogue.texts[key.address]
        return KeyExplained(plain(key.address), key.where, said(text.meaning, language), said(text.accepts, language),
                            key.required, key.enforced, key.rules, said(example_of(key, text.example, names), language),
                            names, tuple(_shown(held, 0, catalogue, language) for held in held_by(key)),
                            tuple(Need(fact, FACTS[fact], supplied(fact, language)) for fact in key.needs),
                            graded_for(key, language), graded(key, language), key.name, holder_of(key),
                            short(key, language), key.read_by)

    def choices(self, key: Key) -> tuple[str, ...]:
        """The bundled profiles, the `testing` presets or the languages, for a key that names one of them; else none."""
        if key.choices == CHOICE_BUNDLED:
            return self._files.bundled()
        if key.choices == CHOICE_LANGUAGES:
            return tuple(sorted(self._files.language_presets()))
        return tuple(self._files.testing_presets()) if key.choices == CHOICE_PRESETS else ()

    def _texts(self) -> Catalogue:
        """The texts of the format, read from its data file once."""
        if self._catalogue is None:
            self._catalogue = catalogue_of(self._files.format_keys())
        return self._catalogue


def _shown(key: Key, depth: int, catalogue: Catalogue, language: Language) -> Shown:
    return Shown(plain(key.address), depth, said(catalogue.texts[key.address].meaning, language), key.required,
                 key.enforced, key.read_by)
