"""The outside-libraries check: code in a part imports only the outside packages `libraries` lists for that part.

The standard library (an import the reader marks as of it) and the app's own package are always allowed, and relative imports
are the app's own; but a module of the standard library the profile reserves is read as an outside package: only a
part that lists it (by its top-level name) may import it, and an import of it or of what lies below it elsewhere is
reported with the profile's reason. Only code in a part is checked: the structure and ungoverned places are not. A
part whose list is EVERYTHING may import any outside package and any reserved module.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import EVERYTHING
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if profile.libraries is None:
        return []
    found: list[Violation] = []
    for file in files:
        src = place(profile, dotted(file.path, profile.language.marks)[0])
        if src is None or src.part is None:
            continue
        allowed = profile.libraries.get(src.part, ())
        if EVERYTHING in allowed:
            continue
        seen: set[tuple[int, str]] = set()
        for imp in file.imports:
            if imp.level or not imp.module:
                continue
            top = imp.module[0]
            reserved = profile.reserved.get(top)
            if top == root or (imp.standard and reserved is None) or top in allowed or (imp.line, top) in seen:
                continue
            seen.add((imp.line, top))
            owners = [name for name, packages in profile.libraries.items() if top in packages and name != src.part]
            fix = (f"move the code that needs {top} to {', '.join(f'{name}/' for name in owners)}, which may import it "
                   f"(parts.{owners[0]}.libraries)" if owners else
                   f"list {top} in the libraries of the part it is reserved for, and keep the code that needs it there"
                   if reserved is not None else
                   f"use the standard library or a package listed in parts.{src.part}.libraries, since {top} is listed "
                   "for no part")
            what = (f"{top}, which the profile reserves: {reserved} (reserved.{top}; parts.{src.part}.libraries)"
                    if reserved is not None else f"the outside package {top} (parts.{src.part}.libraries)")
            found.append(Violation(file.name, imp.line, f"{label(profile, src)} may not import {what}", "libraries",
                                   fix))
    return found
