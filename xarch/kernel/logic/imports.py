"""What a part may import, said in words: the phrase of the docs' rules table, which `xarch where` shows as well.

Consecutive targets in one scope share their phrase: its own <singular>'s `a/` and `b/`, any <singular>'s `c/`, then
those outside the repeating folder; EVERYTHING is "everything", and no target "nothing".
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from xarch.kernel.logic.placement import EVERYTHING, Target


def may_import(targets: Iterable[Target], folders: Mapping[str, str], singular: str) -> str:
    """The targets as a phrase. folders names each part as the docs show it (a path ending in `/` for a folder); the
    part a rule belongs to is left out of the targets by the caller, since its own part is implied."""
    targets = list(targets)
    if any(t.part == EVERYTHING for t in targets):
        return "everything"
    phrases: list[tuple[str, list[str]]] = []
    for target in targets:
        scope = {"own": f"its own {singular}'s ", "any": f"any {singular}'s "}.get(target.scope, "")
        shown = f"`{shown_target(target, folders)}`"
        if scope and phrases and phrases[-1][0] == scope:
            phrases[-1][1].append(shown)
        else:
            phrases.append((scope, [shown]))
    return ", ".join(scope + _and(names) for scope, names in phrases) or "nothing"


def shown_target(target: Target, folders: Mapping[str, str]) -> str:
    """A target as a path: its part's folder, and the path below it if it names one."""
    shown = folders[target.part]
    return shown.removesuffix("/") + "/" + "/".join(target.sub) if target.sub else shown


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"
