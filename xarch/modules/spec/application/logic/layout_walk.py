"""A layout tree walked: its entries, flat, for the skeleton of section 1; whether a path is in it, and whether as a file;
and a part named as the docs name it."""
from __future__ import annotations

from collections.abc import Collection, Iterator

from xarch.kernel.logic.placement import repeat_of
from xarch.modules.spec.domain.published import Entry
from xarch.modules.spec.domain.values import Architecture, Layout, Part


def walk(tree: Layout, prefix: tuple[str, ...] = (), optional: Collection[tuple[str, ...]] = frozenset(),
         when: tuple[str, ...] = ()) -> Iterator[Entry]:
    """Every entry of the tree, parents before children: a leaf is a file, or a folder that holds nothing in it but
    optional parts; optional are the paths of the optional parts, as the entries' are written, and each entry says
    whether it is one and the deepest one it lies in (when, below which the walk starts)."""
    for name, sub in tree.items():
        path = prefix + (name,)
        held = path in optional
        yield Entry(path, sub is not None, all(path + (inner,) in optional for inner in sub or ()), held, when)
        if sub:
            yield from walk(sub, path, optional, path if held else when)


def folders(tree: Layout) -> tuple[tuple[str, ...], ...]:
    """Every folder of a layout, as a path below the app folder: the app folder itself first, then each folder of the
    layout in the order of the walk."""
    return ((), *(entry.path for entry in walk(tree) if entry.is_dir))


def lies_in(tree: Layout, path: tuple[str, ...]) -> bool:
    """Whether a path is in the tree, as a folder or a file."""
    return _at(tree, path)[0]


def is_file(tree: Layout, path: tuple[str, ...]) -> bool:
    """Whether a path of the tree, such as a part's, is a file of it rather than a folder."""
    found, here = _at(tree, path)
    return found and here is None


def docs_name(architecture: Architecture, part: Part) -> str:
    """A part as the docs name it: its path below its instance for an instance's part, ending in / for a folder."""
    repeat = repeat_of(architecture.repeats, part.path)
    path = part.path[len(repeat.root) + 1:] if repeat is not None else part.path
    return "/".join(path) + ("" if is_file(architecture.layout, part.path) else "/")


def _at(tree: Layout, path: tuple[str, ...]) -> tuple[bool, Layout | None]:
    """Whether the path is in the tree, and what is there: the folder's own tree, or None for a file."""
    here: Layout | None = tree
    for step in path:
        if here is None or step not in here:
            return False, None
        here = here[step]
    return True, here
