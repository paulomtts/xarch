"""The shape of a profile file in format 1, read only so that `xarch profile migrate` can convert it. Nothing else
loads format 1: a file that starts with `xarch: 1` is refused by every other command.

The reader checks what the conversion needs to rely on (a layout that is a tree, parts with a path, the repeating folder's
word) and hands everything else on as the file wrote it; the converted profile is validated by the loader of format 2.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.migration import OldPart, OldProfile, Tree

EACH = "*"
KEYS = ("xarch", "name", "layout", "notes", "parts", "rules", "layers", "placement", "naming", "tiers", "docs", "files",
        "examples", "libraries", "fakes", "guards", "tests", "forbidden", "excluded", "hints")
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")

def read_v1(document: Any, source: str) -> OldProfile:
    """The profile in the document; raises InvalidArchitecture listing what cannot be read."""
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys"])
    problems = [f"missing `{key}`" for key in ("layout", "parts") if key not in document]
    singular: list[str] = []
    layout: Tree = {}
    if "layout" in document:
        layout = _tree(document["layout"], "layout", problems, singular)
    parts = _parts(document["parts"], problems) if "parts" in document else {}
    notes = _notes(document["notes"], problems) if "notes" in document else {}
    if problems:
        raise InvalidArchitecture(source, problems)
    extra = tuple(str(key) for key in document if key not in KEYS)
    return OldProfile(str(document.get("name", "")), layout, singular[0] if singular else "", parts, notes, document, extra)


def _tree(value: Any, where: str, problems: list[str], singular: list[str]) -> Tree:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping of folder and file names")
        return {}
    tree: Tree = {}
    if "each" in value:
        word = value.get("singular")
        if isinstance(word, str) and _WORD.fullmatch(word):
            singular.append(word)
        else:
            problems.append(f"{where}: `each` needs `singular` beside it, one word naming an instance")
    for key, sub in value.items():
        if key == "singular" and "each" in value:
            continue
        name = EACH if key == "each" else str(key)
        if sub == "file" and name != EACH:
            tree[name] = None
        else:
            tree[name] = _tree(sub, f"{where}.{key}", problems, singular)
    return tree


def _parts(value: Any, problems: list[str]) -> dict[str, OldPart]:
    if not isinstance(value, Mapping):
        problems.append("parts: must be a mapping of part names to {path, role}")
        return {}
    parts: dict[str, OldPart] = {}
    for name, spec in value.items():
        where = f"parts.{name}"
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `path` and `role`")
            continue
        missing = [key for key in ("path", "role") if key not in spec]
        problems += [f"{where}: missing `{key}`" for key in missing]
        if missing:
            continue
        steps = tuple(str(spec["path"]).strip("/").split("/"))
        parts[str(name)] = OldPart(str(name), steps, str(spec["role"]), str(spec.get("litmus", "")),
                                   spec.get("entry") is True, str(spec.get("untested", "")))
    return parts


def _notes(value: Any, problems: list[str]) -> dict[tuple[str, ...], str]:
    if not isinstance(value, Mapping):
        problems.append("notes: must be a mapping of layout paths to one line of text")
        return {}
    return {tuple(str(key).strip("/").split("/")): str(text) for key, text in value.items()}
