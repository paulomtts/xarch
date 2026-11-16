"""The files a profile points to: what a copy of it must hold to load on its own."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from xarch.modules.spec.domain.values import Architecture


def pointed_files(architecture: Architecture, folders: Mapping[str, Sequence[str]]) -> tuple[str, ...]:
    """Every file below the folder of the profile that its docs, init files and examples name, each once, as a path
    from the profile written with `/`, in the order the profile names them: the templates of the docs, the init files
    (a folder entry as every file under it, as folders lists them by the folder) and the files of the examples."""
    found = [doc.source for doc in architecture.docs if doc.source is not None]
    for entry in architecture.files:
        found += ([f"{entry.source.rstrip('/')}/{name}" for name in folders.get(entry.source, ())] if entry.folder
                  else [entry.source])
    found += [example.file for example in architecture.examples.values()]
    return tuple(name for name in dict.fromkeys(found) if not architecture.language.compiled(name))
