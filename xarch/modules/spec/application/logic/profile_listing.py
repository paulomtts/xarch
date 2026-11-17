"""What the folder holding a profile file holds, as far as the profile names it.

The loader never asks the disk: the service reads which of the files a profile names exist, and which files lie below
the folders it names, and hands the loader that listing. A listing is every such file as its path from the folder
holding the profile, written with `/` as the profile writes it.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from typing import Any


def referenced(document: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The files and the folders a profile names next to it, each as written: every template of
    `docs.pages`, every folder of `docs.examples`, and every `from` of `files`, which is looked up as both, since an
    entry may name a folder where a file is meant; each sorted. What is no mapping or no text is left out: the loader
    reports it."""
    if not isinstance(document, Mapping):
        return (), ()
    files: set[str] = set()
    folders: set[str] = set()
    docs = document.get("docs")
    if isinstance(docs, Mapping):
        files |= {source for _, source in _sources(docs.get("pages"))}
        examples = docs.get("examples")
        folders |= {root for root in examples if isinstance(root, str)} if isinstance(examples, list) else set()
    for key, source in _sources(document.get("files")):
        named = source.removesuffix("/") if isinstance(key, str) and key.endswith("/") else source
        files.add(named)
        folders.add(named)
    return tuple(sorted(files)), tuple(sorted(folders))


def listing(files: Iterable[str], folders: Mapping[str, Iterable[str]]) -> tuple[str, ...]:
    """Every file below each folder, given as its path in that folder, then the files, each as a path from the
    profile's folder, once, in the order given."""
    below = [f"{folder.rstrip('/')}/{name}" for folder, names in folders.items() for name in names]
    return tuple(dict.fromkeys([*below, *files]))


def listing_in(names: Collection[str], folder: str) -> tuple[str, ...] | None:
    """The files of names that lie below folder, as paths in it, in the order of names (the port lists a folder
    sorted); None when none does, as a folder holding no file is no folder to a profile."""
    prefix = folder.rstrip("/") + "/"
    held = tuple(name.removeprefix(prefix) for name in names if name.startswith(prefix))
    return held or None


def _sources(value: Any) -> list[tuple[Any, str]]:
    if not isinstance(value, Mapping):
        return []
    found = [(key, spec) if isinstance(spec, str) else (key, spec.get("from")) for key, spec in value.items()
             if isinstance(spec, str) or isinstance(spec, Mapping)]
    return [(key, source) for key, source in found if isinstance(source, str)]
