"""How well a language's reader supplies the facts a key or a rule needs: the facts it needs that the reader supplies
partly or not at all (the facts and their grades are the vocabulary of capabilities in profile_values/)."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from xarch.profile_values.capabilities import EXACT, Shortfall, Supply


def shortfalls(address: str, needs: Iterable[str], supplies: Mapping[str, Supply]) -> list[Shortfall]:
    """The facts a key at address needs that the language does not supply exactly, in the order of the needs."""
    return [Shortfall(address, fact, None if fact not in supplies else supplies[fact].note) for fact in needs
            if fact not in supplies or supplies[fact].grade != EXACT]
