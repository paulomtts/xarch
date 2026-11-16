"""How a profile writes a target, a place a part may import or a check names: `<part>`, `<part>@any`,
`<part>/<path>` and, where a pattern is allowed, `<part>:<pattern>`; checked against the parts declared, each by its
path, and the part that writes it, each problem said at its address. Spec reads a part's `may_import` with it, and
rules the places a check of the profile's own names; each writes a target back with target_written()."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.logic.placement import root_of
from xarch.kernel.placement import EACH
from xarch.profile_values.placement import Target

WORD = "everything"
"""How a file writes EVERYTHING: for what a part may import and for its libraries."""
TARGET = re.compile(r"(?P<part>[^@/:]*)(?:@(?P<scope>[^/:]*))?(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?")
NAME_PATTERN = re.compile(r"[A-Za-z0-9_*]+")


def target(value: Any, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
           declared: Collection[str], where: str, problems: list[str], patterns: bool = False) -> Target | None:
    """The target a profile writes as value, for the part owner (its name and path; None for a tier's folder or a
    scope of no part), each part by its path; None, with the problem said at where, when it is not one. A target that
    names a part declared but not placed is None, with no problem of its own."""
    if value == WORD:
        problems.append(f"{where}: {value!r} stands alone: write `may_import: {WORD}`, not in a list")
        return None
    match = TARGET.fullmatch(value) if isinstance(value, str) else None
    if match is None or not match["part"]:
        problems.append(f"{where}: {value!r} is not a target: use <part>, <part>@any, optionally followed by /<path>")
        return None
    name, scope, sub, names = match["part"], match["scope"], match["sub"], match["names"]
    if names is not None and not patterns:
        problems.append(f"{where}: {value!r} has a name pattern: only a part's `may_import` narrows what may be "
                        "imported by name")
        return None
    if names is not None and not names:
        problems.append(f"{where}: {value!r} has an empty name pattern after `:`")
        return None
    if names is not None and not NAME_PATTERN.fullmatch(names):
        problems.append(f"{where}: {value!r} has a name pattern that is not one: use letters, digits, '_' and `*`")
        return None
    path = parts.get(name)
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    in_instance = EACH in path
    owned = owner is not None and EACH in owner[1]
    if scope is not None and scope not in ("own", "any"):
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': the only scope is @any, any instance of "
                        "the repeating folder")
        return None
    inside = owner is not None and owned and root_of(owner[1]) == root_of(path)
    if in_instance and scope == "own" and inside:
        problems.append(f"{where}: {value!r} says what a bare name already says: write {name}")
        return None
    if in_instance and not inside and scope != "any":
        if owner is not None and owned:
            problems.append(f"{where}: {value!r} lies in another repeating folder than part '{owner[0]}', which has "
                            f"no own instance of it: write {name}@any")
            return None
        importer = f"{owner[0]} is" if owner is not None else "a tier's folder is"
        problems.append(f"{where}: {value!r} lies in the repeating folder, which {importer} not in: say {name}@any")
        return None
    if not in_instance and scope is not None:
        problems.append(f"{where}: {value!r} does not lie in the repeating folder: drop '@{scope}'")
        return None
    steps = tuple(sub.split("/")) if sub is not None else ()
    if any(not step or step in (".", "..") or EACH in step for step in steps):
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    chosen = "any" if scope == "any" else ("own" if in_instance else "none")
    if owner is not None and name == owner[0] and chosen != "any":
        problems.append(implied(where, value, owner))
        return None
    return Target(name, chosen, steps, names or "")


def target_written(made: Target) -> str:
    """The target as a profile writes it, which target() reads back: `@any` for any instance of the repeating folder
    (a bare name is the importer's own instance, or no instance), then the path below the part and the name pattern."""
    return (made.part + ("@any" if made.scope == "any" else "") + ("/" + "/".join(made.sub) if made.sub else "")
            + (f":{made.names}" if made.names else ""))


def implied(where: str, value: str, part: tuple[str, tuple[str, ...]]) -> str:
    """A part may always import itself, so a target that only says so is refused: the part by its name and path."""
    if EACH not in part[1]:
        return f"{where}: {value!r} is implied: a part may always import itself; remove it"
    return (f"{where}: {value!r} is implied: a part may always import itself, its own instance of the repeating "
            f"folder; remove it ({part[0]}@any, another instance's too, stays allowed)")
