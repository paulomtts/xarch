"""The skeleton of section 1 as flat entries walked from an architecture's layout."""
from __future__ import annotations

from collections.abc import Iterator

from xarch.modules.spec.domain.values import Layout


def walk(tree: Layout, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], bool, bool]]:
    """Yield (path, is_dir, is_leaf) for every entry, parents before children.

    A leaf is a file, or a directory that holds nothing in the spec.
    """
    for name, sub in tree.items():
        path = prefix + (name,)
        yield path, sub is not None, not sub
        if sub:
            yield from walk(sub, path)
