"""Where code sits in the architecture, and the dependency rules of docs/project/architecture.md section 5."""
from __future__ import annotations

from dataclasses import dataclass

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
    if src.part == "bootstrap":
        return True
    if dst.part == "structure":
        return False
    if dst.part == "kernel":
        return src.part != "structure"
    same = src.module is not None and src.module == dst.module
    match src.part:
        case "platform":
            return dst.part == "platform"
        case "entry":
            return dst.part == "entry" or (dst.part in ("controller", "contract") and dst.module is not None)
        case "domain":
            return same and dst.part == "domain"
        case "contract":
            return same and (dst.part == "contract" or (dst.part == "domain" and dst.sub[:1] == ("values",)))
        case "controller":
            return same and dst.part in ("controller", "services", "logic", "ports", "domain", "contract")
        case "services":
            return same and dst.part in ("services", "logic", "ports", "domain", "contract")
        case "logic":
            return same and dst.part in ("logic", "domain")
        case "ports":
            return same and dst.part in ("ports", "domain")
        case "adapters":
            if dst.part == "platform":
                return True
            if dst.part == "contract":
                return True            # its own, or the provider's whose controller it wraps (section 6)
            return same and dst.part in ("adapters", "ports", "domain")
    return False
