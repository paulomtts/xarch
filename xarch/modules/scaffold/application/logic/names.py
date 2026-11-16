"""Which names `new` gives an instance of a repeating folder."""
from __future__ import annotations

from xarch.kernel.logic.names import is_public_name
from xarch.modules.scaffold.domain.values import Language


def valid_name(name: str, language: Language) -> bool:
    """A lowercase name in plain letters that the language allows, neither private nor reserved."""
    return (name.isascii() and name == name.lower() and is_public_name(name, language.names, language.private)
            and name not in language.reserved)
