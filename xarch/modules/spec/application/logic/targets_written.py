"""How a profile writes a target of what may be imported, and the targets it writes as a list: `<part>`, `<part>@any`,
`<part>/<path>` and, where a pattern is allowed, `<part>:<pattern>`; checked against the parts declared and the part
that writes them (None for a tier's folder or a scope of no part), each problem said at its address."""
from __future__ import annotations

import re
from typing import Any

from xarch.kernel.logic.placement import root_of
from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.domain.values import EACH, Part, Target

WORD = "everything"
"""How a file writes EVERYTHING: for what a part may import and for its libraries."""
TARGET = re.compile(r"(?P<part>[^@/:]*)(?:@(?P<scope>[^/:]*))?(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?")
NAME_PATTERN = re.compile(r"[A-Za-z0-9_*]+")


def may_import(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
                problems: list[str], patterns: bool = False) -> tuple[Target, ...]:
    """What a part, or the tests in a tier's folder (no owner), may import, as targets; a name pattern only where
    patterns allows one."""
    if value is None:
        return ()
    if value == WORD:
        return (Target(EVERYTHING),)
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of targets such as [<part>, shared/text, api@any], or {WORD}")
        return ()
    found: list[Target] = []
    for item in value:
        written = target(item, owner, parts, declared, where, problems, patterns)
        if written is not None:
            found.append(written)
    return tuple(found)


def target(value: Any, owner: Part | None, parts: dict[str, Part], declared: set[str], where: str,
            problems: list[str], patterns: bool = False) -> Target | None:
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
    part = parts.get(name)
    if part is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    if scope is not None and scope not in ("own", "any"):
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': the only scope is @any, any instance of "
                        "the repeating folder")
        return None
    inside = owner is not None and owner.in_instance and root_of(owner.path) == root_of(part.path)
    if part.in_instance and scope == "own" and inside:
        problems.append(f"{where}: {value!r} says what a bare name already says: write {name}")
        return None
    if part.in_instance and not inside and scope != "any":
        if owner is not None and owner.in_instance:
            problems.append(f"{where}: {value!r} lies in another repeating folder than part '{owner.name}', which has "
                            f"no own instance of it: write {name}@any")
            return None
        importer = f"{owner.name} is" if owner is not None else "a tier's folder is"
        problems.append(f"{where}: {value!r} lies in the repeating folder, which {importer} not in: say {name}@any")
        return None
    if not part.in_instance and scope is not None:
        problems.append(f"{where}: {value!r} does not lie in the repeating folder: drop '@{scope}'")
        return None
    steps = tuple(sub.split("/")) if sub is not None else ()
    if any(not step or step in (".", "..") or EACH in step for step in steps):
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    chosen = "any" if scope == "any" else ("own" if part.in_instance else "none")
    if owner is not None and name == owner.name and chosen != "any":
        problems.append(implied(where, value, owner))
        return None
    return Target(name, chosen, steps, names or "")


def implied(where: str, value: str, part: Part) -> str:
    """A part may always import itself, so a target that only says so is refused."""
    if not part.in_instance:
        return f"{where}: {value!r} is implied: a part may always import itself; remove it"
    return (f"{where}: {value!r} is implied: a part may always import itself, its own instance of the repeating "
            f"folder; remove it ({part.name}@any, another instance's too, stays allowed)")
