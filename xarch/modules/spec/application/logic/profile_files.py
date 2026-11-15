"""The files a profile points to: what a copy of it must hold to load on its own."""
from __future__ import annotations

from collections.abc import Callable, Collection

from xarch.modules.spec.domain.profile_examples import PYCACHE
from xarch.modules.spec.domain.values import Architecture


def pointed_files(architecture: Architecture, folder_files: Callable[[str], tuple[str, ...]]) -> tuple[str, ...]:
    """Every file below the folder of the profile that its docs, init files and examples name, each once, as a path
    from the profile written with `/`, in the order the profile names them: the templates of the docs, the init files
    (a folder entry as every file under it, folder_files says which) and the files of the examples."""
    found = [doc.source for doc in architecture.docs if doc.source is not None]
    for entry in architecture.files:
        found += [f"{entry.source.rstrip('/')}/{name}" for name in folder_files(entry.source)] if entry.folder else [entry.source]
    found += [example.file for example in architecture.examples.values()]
    return tuple(name for name in dict.fromkeys(found) if PYCACHE not in name.split("/"))


def listing_in(names: Collection[str], folder: str) -> tuple[str, ...] | None:
    """The files of names that lie below folder, as paths in it, sorted; None when none does, as a folder holding no
    file is no folder to a profile."""
    prefix = folder.rstrip("/") + "/"
    held = tuple(sorted(name.removeprefix(prefix) for name in names if name.startswith(prefix)))
    return held or None
