"""What an import reaches: a file's dotted path below the root, and the file or package below the root each import
into the root package names, read as a file when it is one. The checks read it through the facts (see facts); the
rules of what a part may import are rules as data (see expansion.rules)."""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.kernel.logic.source import relative_target
from xarch.kernel.placement import Marks
from xarch.kernel.source import Import


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

