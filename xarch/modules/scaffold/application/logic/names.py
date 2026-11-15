"""Which names `new` gives an instance of a repeating folder."""
from __future__ import annotations

import re

from xarch.modules.scaffold.domain.values import Language


def valid_name(name: str, language: Language) -> bool:
    """A lowercase name in plain letters that the language allows, neither private nor reserved."""
    return (name.isascii() and bool(re.fullmatch(language.names or ".+", name)) and name == name.lower()
            and not (language.private and name.startswith(language.private)) and name not in language.reserved)
