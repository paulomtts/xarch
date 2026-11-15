"""The examples of a profile file (format version 2): `docs.examples` lists folders next to the profile, each an
example project, and every file below one is an example, named by its path in the project. A template quotes one with
`{{example:<path>}}`, a tier shows one as its example or helper by the same path, and `docs.example_notes` says
something after a path. Which part an example illustrates is the part its path lies in."""
from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.profile_listing import listing_in
from xarch.modules.spec.domain.values import EACH, Architecture, Example, Language, Layout, Part, TierExample


@dataclass
class Examples:
    """files: the file of each example, relative to the profile, by its path in its project; notes: by the same path."""
    files: dict[str, str] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)


def example_files(docs: Any, files: Collection[str], problems: list[str], language: Language) -> Examples:
    """The files below the folders `docs.examples` lists, and their notes; a docs that is no mapping is reported
    elsewhere."""
    found = Examples()
    if not isinstance(docs, Mapping):
        return found
    if "examples" in docs:
        _roots(docs["examples"], files, found, problems, language)
    if "example_notes" in docs:
        _notes(docs["example_notes"], found, problems)
    return found


def _roots(value: Any, files: Collection[str], found: Examples, problems: list[str], language: Language) -> None:
    if not isinstance(value, list):
        problems.append("docs.examples: must be a list of folders next to the profile file, each an example project, "
                        "such as [examples/shared]")
        return
    owners: dict[str, str] = {}
    clashes: list[str] = []
    for i, root in enumerate(value):
        where = f"docs.examples[{i}]"
        if not ck.text(root):
            problems.append(f"{where}: must be a folder next to the profile file, such as examples/shared")
            continue
        listing = listing_in(files, root)
        if not listing:
            problems.append(f"{where}: no folder '{root}' holding a file next to the profile file")
            continue
        for relative in listing:
            if language.cache and language.cache in relative.split("/"):
                continue
            if relative in owners:
                clashes.append(f"docs.examples: '{relative}' is in both '{owners[relative]}' and '{root}': an example "
                               "is named by its path in its project")
                continue
            owners[relative] = root
            found.files[relative] = f"{root.strip('/')}/{relative}"
    problems += clashes


def _notes(value: Any, found: Examples, problems: list[str]) -> None:
    if not isinstance(value, Mapping):
        problems.append("docs.example_notes: must be a mapping of paths in an example project to one line of text")
        return
    for key, note in value.items():
        where = f"docs.example_notes.{key}"
        if str(key) not in found.files:
            problems.append(f"{where}: no file '{key}' in any folder of docs.examples")
        elif not ck.line(note):
            problems.append(f"{where}: must be one line of text")
        else:
            found.notes[str(key)] = note


def example_of(value: Any, found: Examples, where: str, problems: list[str], language: Language) -> TierExample | None:
    """A tier's example or helper, written as the path of a file of an example project; its note, if any, is the plain text
    of `docs.example_notes`."""
    steps = tuple(value.strip("/").split("/")) if ck.text(value) else ()
    if not steps or any(step in ("", ".", "..") or EACH in step or "<" in step or "\\" in step for step in steps):
        problems.append(f"{where}: must be a path in an example project, such as src/billing/charge{language.extension}")
        return None
    path = "/".join(steps)
    if path not in found.files:
        problems.append(f"{where}: no file '{path}' in any folder of docs.examples")
        return None
    return TierExample(steps, found.files[path], found.notes.get(path, ""))


def examples_of(found: Examples, layout: Layout, parts: dict[str, Part], language: Language) -> dict[str, Example]:
    """Every example, in the order of the folders and then of the files: its part is the part its path lies in, none
    (empty) for test code and anything else no part claims."""
    shaped = Architecture("", layout, parts, {}, language=language)
    examples: dict[str, Example] = {}
    for path, file in found.files.items():
        steps = tuple(path.split("/"))
        examples[path] = Example(path, shaped.place_of(steps).part or "", steps, file, found.notes.get(path, ""))
    return examples
