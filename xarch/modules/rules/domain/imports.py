"""The import check itself: every import between places the profile governs must be allowed by its rules.

Files in places the profile does not govern are not checked, and imports into such places are ignored.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.kernel.logic.placement import EVERYTHING, Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.places import allowed, label, place, targets_of
from xarch.modules.rules.domain.values import Import, Profile, SourceFile

OWNERS = 3
"""How many parts that may import a place a fix names before it says "or another part"."""


def dotted(path: tuple[str, ...]) -> tuple[tuple[str, ...], bool]:
    """A file's dotted path below the root, and whether it is a package's __init__."""
    steps = path[:-1] + (path[-1].removesuffix(".py"),) if path else path
    is_package = bool(steps) and steps[-1] == "__init__"
    return (steps[:-1] if is_package else steps), is_package


def targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
            root: str) -> Iterator[tuple[int, tuple[str, ...]]]:
    """Yield (line, absolute path below the root package) for every import that points into it.

    `from m import n` names the module m.n when it is a known file, else the module m.
    """
    for imp in imports:
        if imp.names is None:
            if imp.module[:1] == (root,):
                yield imp.line, imp.module[1:]
            continue
        if imp.level:
            keep = len(package) - (imp.level - 1)
            if keep < 0:
                continue
            base = package[:keep] + imp.module
        else:
            if imp.module[:1] != (root,):
                continue
            base = imp.module[1:]
        for name in imp.names:
            candidate = base + (name,)
            yield imp.line, candidate if candidate in known else base


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    """Check files below the root package named root against the profile's rules."""
    parsed = [(f, *dotted(f.path)) for f in files]
    known = {steps for _, steps, _ in parsed}
    found: list[Violation] = []
    for file, steps, is_package in parsed:
        src = place(profile, steps)
        if src is None:
            continue
        package = steps if is_package else steps[:-1]
        for line, target in targets(file.imports, package, known, root):
            dst = place(profile, target)
            if dst is not None and not allowed(profile, src, dst):
                shown = ".".join((root, *target))
                found.append(Violation(file.name, line, f"{label(profile, src)} may not import {label(profile, dst)} ({shown})",
                                       "rules", _fix(profile, src, dst)))
    return found


def _fix(profile: Profile, src: Place, dst: Place) -> str:
    """What to do about an import that rules forbid: import what the part may, or move the code to a part that may
    import the place; both named from the profile."""
    targets_of_src = targets_of(profile, src.part) if src.part is not None else ()
    permitted = list(dict.fromkeys(t.part for t in targets_of_src if t.part != EVERYTHING))
    owners = [name for name, targets in profile.rules.items()
              if name not in (src.part, dst.part) and any(t.part == dst.part for t in targets)]
    shown = ", ".join(f"{name}/" for name in owners[:OWNERS])
    move = (f"move this code to {shown}, which may import it" if 0 < len(owners) <= OWNERS else
            f"move this code to {shown} or another part that may import it" if owners else
            f"move this code to a part that may import {label(profile, dst)}")
    if not permitted:
        return f"drop the import of {label(profile, dst)}, or {move}"
    return (f"import only {', '.join(f'{name}/' for name in permitted)} in {label(profile, src)} "
            f"(rules.{src.part}), or {move}")
