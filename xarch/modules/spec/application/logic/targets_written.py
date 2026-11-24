"""What a part, or the tests in a tier's folder, may import, as a profile writes it: a list of targets, each a reference
(see the target grammar in kernel/logic/targets), parts.<part> or <word>.<part>, the word one of the profile's
repeating folders, or `everything`; checked against the parts declared and the part that writes them (None for a
tier's folder), each problem said at its address. What a tier's tests may also import is a list of targets alone,
<word>.<part> being the instance a test mirrors."""
from __future__ import annotations

from collections.abc import Collection
from typing import Any

from xarch.kernel.logic.targets import target
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target

WORD = "everything"
"""How a file writes EVERYTHING: for what a part may import and for its libraries."""


def allowed_targets(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
                    problems: list[str], patterns: bool = False, mirrored: bool = False, *,
                    repeats: Collection[Repeat]) -> tuple[Target, ...]:
    """What a part, or the tests in a tier's folder (no owner), may import, as targets, a reference's word one of
    repeats, the profile's repeating folders; a name pattern only where patterns allows one; when mirrored, what a
    tier's tests may also import, read from the instance a test mirrors."""
    if value is None:
        return ()
    if value == WORD and not mirrored:
        return (Target(EVERYTHING),)
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of targets such as [parts.core, unit.store/schema]"
                        + (f": `{WORD}` is not taken, name each target the tests may also import" if mirrored
                           else f", or {WORD}"))
        return ()
    paths = _paths_of(parts)
    found: list[Target] = []
    for item in value:
        if item == WORD:
            problems.append(f"{where}: `{WORD}` is not taken, name each target the tests may also import" if mirrored
                            else f"{where}: {item!r} stands alone: write `{WORD}` in place of the list")
            continue
        written = target(item, None if owner is None else (owner.name, owner.path), paths, declared, where, problems,
                         patterns, mirrored, alone="a tier's folder", repeats=repeats)
        if written is not None:
            found.append(written)
    return tuple(found)


def _paths_of(parts: dict[str, Part]) -> dict[str, tuple[str, ...]]:
    """Each part by its path, as the target grammar reads them."""
    return {name: part.path for name, part in parts.items()}
