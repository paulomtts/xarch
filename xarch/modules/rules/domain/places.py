"""Where code sits in the architecture, and the dependency rules of docs/project/architecture.md section 5."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.modules.rules.domain.rules_table import EVERYTHING, RULES, Target
from xarch.modules.rules.domain.values import Parts


@dataclass(frozen=True)
class Place:
    part: str                      # kernel, platform, entry, bootstrap, structure, or a part of a module
    module: str | None = None      # the bounded module, for module parts
    sub: tuple[str, ...] = ()      # path below the part, e.g. ("values",) for domain/values.py
    folder: str = ""               # how the part is named when it is not its own folder: the entry point's


def place_of(parts: tuple[str, ...], layout: Parts) -> Place | None:
    """Where a dotted path below the root package sits in the architecture, or None if the profile does not govern it."""
    if not parts or parts == ("modules",) or (len(parts) == 2 and parts[0] == "modules"):
        return Place("structure")
    if parts[0] == layout.entry_point:
        return Place("entry", None, parts[1:], layout.entry_point)
    if parts[0] in layout.top_level:
        return Place(parts[0], None, parts[1:])
    if parts[0] != "modules":
        return None
    module, rest = parts[1], parts[2:]
    if rest == ("application",):
        return Place("structure")
    if rest and rest[0] in layout.module_folders:
        return Place(rest[0], module, rest[1:])
    if len(rest) >= 2 and rest[0] == "application" and rest[1] in layout.application_parts:
        return Place(rest[1], module, rest[2:])
    return None


def label(place: Place) -> str:
    return f"{place.folder or place.part}/" + (f" of module '{place.module}'" if place.module else "")


def allowed(src: Place, dst: Place) -> bool:
    return any(_reaches(target, src, dst) for target in RULES.get(src.part, ()))


def _reaches(target: Target, src: Place, dst: Place) -> bool:
    if target.part == EVERYTHING:
        return True
    if target.part != dst.part or dst.sub[:len(target.sub)] != target.sub:
        return False
    match target.scope:
        case "own":
            return src.module is not None and src.module == dst.module
        case "any":
            return dst.module is not None
        case "none":
            return dst.module is None
    return False
