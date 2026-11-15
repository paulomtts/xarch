"""The outside-libraries check: code in a part imports only the outside packages `libraries` lists for that part.

The standard library (sys.stdlib_module_names) and the app's own package are always allowed, and relative imports
are the app's own. Only code in a part is checked: the structure and ungoverned places are not.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if profile.libraries is None:
        return []
    found: list[Violation] = []
    for file in files:
        src = place(profile, dotted(file.path)[0])
        if src is None or src.part is None:
            continue
        allowed = profile.libraries.get(src.part, ())
        seen: set[tuple[int, str]] = set()
        for imp in file.imports:
            if imp.level or not imp.module:
                continue
            top = imp.module[0]
            if top == root or top in sys.stdlib_module_names or top in allowed or (imp.line, top) in seen:
                continue
            seen.add((imp.line, top))
            found.append(Violation(file.name, imp.line, f"{label(profile, src)} may not import the outside package "
                                                        f"{top} (libraries.{src.part})"))
    return found
