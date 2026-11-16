"""What an import reaches: a file's dotted path below the root, and the file or package below the root each import
into the root package names, read as a file when it is one. The checks read it through the facts (see facts); the
rules of what a part may import are rules as data (the "rules" rules of expansion.book)."""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.kernel.logic.placement import module_steps, stands_for_folder
from xarch.kernel.logic.source import imported_names
from xarch.kernel.placement import Marks
from xarch.kernel.source import Import


def dotted(path: tuple[str, ...], marks: Marks) -> tuple[tuple[str, ...], bool]:
    """A file's dotted path below the root, and whether it is the file that stands for its folder."""
    return module_steps(path, marks), stands_for_folder(path, marks)


def targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
            root: str) -> Iterator[tuple[int, tuple[str, ...]]]:
    """Yield (line, absolute path below the root package) for every import that points into it.

    An import that takes the name n from the module m names the module m.n when it is a known file, else the module m.
    """
    for line, target, _ in named_targets(imports, package, known, root):
        yield line, target


def named_targets(imports: Iterable[Import], package: tuple[str, ...], known: set[tuple[str, ...]],
                  root: str) -> Iterator[tuple[int, tuple[str, ...], str | None]]:
    """What targets yields, with the name imported from the target: n for an import that takes n from the module m
    when m.n is no known file, else None, the target imported as a whole."""
    for imp in imports:
        for base, name in imported_names(imp, package, root):
            if name is None or base + (name,) in known:
                yield imp.line, base if name is None else base + (name,), None
            else:
                yield imp.line, base, name

