"""Which names `new` gives an instance of a repeating folder."""
from __future__ import annotations

from xarch.kernel.logic.names import is_name, is_private_name
from xarch.modules.scaffold.domain.values import LOWERCASE, NOT_A_NAME, PRIVATE, RESERVED, Language


def broken_rule(name: str, language: Language) -> str | None:
    """The first rule of a name of a new instance the name breaks: a lowercase name in plain letters (LOWERCASE), that
    the language allows (NOT_A_NAME), not private (PRIVATE) and not reserved (RESERVED); None when it breaks none."""
    if not (name.isascii() and name == name.lower()):
        return LOWERCASE
    if not is_name(name, language.names):
        return NOT_A_NAME
    if is_private_name(name, language.private):
        return PRIVATE
    if name in language.reserved:
        return RESERVED
    return None
