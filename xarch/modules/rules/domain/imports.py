"""The import check itself: every import between places the profile governs must be allowed by section 5.

xarch is a protocol, not a closed world: files in places the profile does not govern are not checked, and
imports into such places are ignored.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import PurePosixPath

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.places import allowed, label, place_of
from xarch.modules.rules.domain.values import Import, Parts, SourceFile


def _dotted(path: tuple[str, ...]) -> tuple[tuple[str, ...], bool]:
    parts = PurePosixPath(*path).with_suffix("").parts
    is_package = parts[-1] == "__init__"
    return (parts[:-1] if is_package else parts), is_package


def _targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
             root: str) -> Iterator[tuple[int, tuple[str, ...]]]:
    """Yield (line, absolute path below the root package) for every import that points into it."""
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


def violations(files: Iterable[SourceFile], layout: Parts, root: str) -> list[Violation]:
    """Check files below the root package named root; layout gives the folder names that place code."""
    parsed = [(f, *_dotted(f.path)) for f in files]
    known = {parts for _, parts, _ in parsed}
    found: list[Violation] = []
    for file, parts, is_package in parsed:
        src = place_of(parts, layout)
        if src is None:
            continue
        package = parts if is_package else parts[:-1]
        for line, target in _targets(file.imports, package, known, root):
            dst = place_of(target, layout)
            shown = f"{root}.{'.'.join(target)}"
            if dst is not None and not allowed(src, dst):
                found.append(Violation(file.name, line, f"{label(src)} may not import {label(dst)} ({shown})"))
    return found
