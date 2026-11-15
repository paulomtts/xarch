"""The import check itself: every import between places the profile governs must be allowed by its rules.

Files in places the profile does not govern are not checked, and imports into such places are ignored. A target of
the rules with a name pattern allows only `from <place> import <name>` for a name the pattern matches: a name that does
not match, and an import of the place's file as a whole (`import m`, or `from <package> import m` for its file m), is
reported, naming the pattern.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import replace

from xarch.kernel.logic.placement import EVERYTHING, Marks, Place, reaches
from xarch.kernel.logic.source import Import, relative_target
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.places import allowed, label, place, targets_of
from xarch.modules.rules.domain.values import Profile, SourceFile

OWNERS = 3
"""How many parts that may import a place a fix names before it says "or another part"."""


def dotted(path: tuple[str, ...], marks: Marks) -> tuple[tuple[str, ...], bool]:
    """A file's dotted path below the root, and whether it is the file that stands for its folder."""
    steps = path[:-1] + (path[-1].removesuffix(marks.extension),) if path else path
    stem = marks.package_file.removesuffix(marks.extension)
    is_package = bool(steps) and bool(stem) and steps[-1] == stem
    return (steps[:-1] if is_package else steps), is_package


def targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
            root: str) -> Iterator[tuple[int, tuple[str, ...]]]:
    """Yield (line, absolute path below the root package) for every import that points into it.

    `from m import n` names the module m.n when it is a known file, else the module m.
    """
    for line, target, _ in named_targets(imports, package, known, root):
        yield line, target


def named_targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
                  root: str) -> Iterator[tuple[int, tuple[str, ...], str | None]]:
    """What targets yields, with the name imported from the target: n for `from m import n` when m.n is no known file,
    else None, the target imported as a whole."""
    for imp in imports:
        if imp.names is None:
            if imp.module[:1] == (root,):
                yield imp.line, imp.module[1:], None
            continue
        if imp.relative:
            base = relative_target(imp, package)
            if base is None:
                continue
        else:
            if imp.module[:1] != (root,):
                continue
            base = imp.module[1:]
        for name in imp.names:
            candidate = base + (name,)
            yield (imp.line, candidate, None) if candidate in known else (imp.line, base, name)


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    """Check files below the root package named root against the profile's rules."""
    parsed = [(f, *dotted(f.path, profile.language.marks)) for f in files]
    known = {steps for _, steps, _ in parsed}
    found: list[Violation] = []
    for file, steps, is_package in parsed:
        src = place(profile, steps)
        if src is None:
            continue
        package = steps if is_package else steps[:-1]
        for line, target, name in named_targets(file.imports, package, known, root):
            dst = place(profile, target)
            if dst is None or allowed(profile, src, dst, name):
                continue
            shown = ".".join((root, *target, *([name] if name is not None else [])))
            patterns = _patterns(profile, src, dst)
            if patterns:
                what = f"not {name}" if name is not None else "not the file as a whole"
                found.append(Violation(file.name, line, f"{label(profile, src)} may import only {patterns} from "
                                                        f"{label(profile, dst)}, {what} ({shown})", "rules",
                                       f"import from {label(profile, dst)} only names that match {patterns} "
                                       f"(parts.{src.part}.may_import), or move what needs the rest to a part that "
                                       "may import it"))
            else:
                found.append(Violation(file.name, line, f"{label(profile, src)} may not import {label(profile, dst)} "
                                                        f"({'.'.join((root, *target))})", "rules",
                                       _fix(profile, src, dst)))
    return found


def _patterns(profile: Profile, src: Place, dst: Place) -> str:
    """The name patterns of the targets that reach the place but for their pattern, as "*Id or *Key"; "" for none."""
    narrowed = [t.names for t in (targets_of(profile, src.part) if src.part is not None else ())
                if t.names and reaches(replace(t, names=""), src, dst)]
    return " or ".join(dict.fromkeys(narrowed))


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
            f"(parts.{src.part}.may_import), or {move}")
