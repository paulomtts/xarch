"""A layout tree walked: its entries, flat, for the skeleton of section 1; whether a path is in it, and whether as a file;
and a part named as the docs name it."""
from __future__ import annotations

from collections.abc import Iterator

from xarch.kernel.logic.placement import repeat_of
from xarch.modules.spec.domain.values import Architecture, Layout, Part


def walk(tree: Layout, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], bool, bool]]:
    """Yield (path, is_dir, is_leaf) for every entry, parents before children.

    A leaf is a file, or a directory that holds nothing in the spec.
    """
    for name, sub in tree.items():
        path = prefix + (name,)
        yield path, sub is not None, not sub
        if sub:
            yield from walk(sub, path)


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
