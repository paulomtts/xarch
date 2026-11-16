"""How a filter is written, as a check of the profile's own and a rule of xarch's name it: `[not ]<name>[ <value>]`.
Spec reads a check's filters with it, and rules its built-in rules' filters."""
from __future__ import annotations

from xarch.profile_values.checks import NEGATION, Condition


def condition(text: str) -> Condition:
    """The condition text writes: `[not ]<name>[ <value>]`."""
    negated = text.startswith(NEGATION)
    name, _, value = text.removeprefix(NEGATION).partition(" ")
    return Condition(name, value, negated)
