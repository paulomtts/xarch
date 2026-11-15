"""The files of a profile in format 1 that a profile in format 2 holds differently: the docs' templates, the files `init`
writes and the examples. Format 2 lists folders of example projects and names an example by its path in the project, so
every example file is copied to that path below one folder, and a template quotes it by the path."""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

PLACEHOLDER = re.compile(r"\{\{example:(.*?)\}\}")
ROOT = "examples"


@dataclass(frozen=True)
class Copy:
    """A file of the converted folder: where it goes, the file next to the old profile it is read from, and whether its
    example placeholders are rewritten."""
    destination: str
    source: str
    rewritten: bool = False


@dataclass
class Gathered:
    """pages and files: the converted values of `docs` and `files`; names: each example's name with its path; notes:
    each path with its plain note; tiers: for each tier, its example's path (or None) and its helpers' paths."""
    copies: list[Copy] = field(default_factory=list)
    names: dict[str, str] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)
    root: str = ""
    pages: dict[str, Any] = field(default_factory=dict)
    files: dict[str, Any] = field(default_factory=dict)
    tiers: dict[str, tuple[str | None, list[str]]] = field(default_factory=dict)


@dataclass(frozen=True)
class _Item:
    label: str
    path: str
    source: str
    note: str
    plain: bool


def rewrite_examples(text: str, names: dict[str, str]) -> tuple[str, tuple[str, ...]]:
    """The text with each `{{example:<name>, ...}}` naming the paths of the examples, and the names no example has,
    which stay as written."""
    unknown: list[str] = []

    def replace(match: re.Match[str]) -> str:
        chosen = [name.strip() for name in match[1].split(",")]
        if any(name not in names for name in chosen):
            unknown.extend(name for name in chosen if name not in names)
            return match[0]
        return "{{example:" + ", ".join(names[name] for name in chosen) + "}}"

    return PLACEHOLDER.sub(replace, text), tuple(unknown)


def plain_note(note: str, label: str, changes: list[str]) -> str:
    """A note of format 1 that was shown right after a path as written: its text without the outer parentheses."""
    text = note.strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    stripped = text.strip(":;,- ").strip()
    changes.append(f"{label}: the note {note!r} was shown after the path as written; format 2 shows it in "
                   f"parentheses as {stripped!r}")
    return stripped


def gather(old: Any, tiers: list[Any], has_file: Callable[[str], bool],
           folder_files: Callable[[str], tuple[str, ...]], changes: list[str], by_hand: list[str]) -> Gathered:
    """Everything the old profile names as a file, converted."""
    items = _items(old, tiers, has_file, changes, by_hand)
    held = {item.source for item in items}
    plain = _sources(old, held, has_file, folder_files, by_hand)
    root = _root(plain)
    found = Gathered(root=root if items else "")
    taken: dict[str, str] = {}

    def copy(destination: str, source: str, label: str, rewritten: bool = False) -> bool:
        if taken.get(destination, source) != source:
            by_hand.append(f"{label}: '{source}' would be copied to '{destination}', which '{taken[destination]}' "
                           "already takes: give one of them another path")
            return False
        if destination not in taken:
            taken[destination] = source
            found.copies.append(Copy(destination, source, rewritten))
        return True

    for key, spec in _entries(old.get("docs")):
        source = spec.get("from")
        if source is not None and not has_file(source):
            by_hand.append(f"docs.{key}: no file '{source}' next to the profile: the page is not converted")
            continue
        found.pages[key] = _page(spec)
        if source is not None:
            copy(source, source, f"docs.{key}", True)
    pending: dict[str, dict[str, Any]] = {}
    for key, spec in _entries(old.get("files")):
        source = spec.get("from", "")
        if key.endswith("/"):
            found.files[key] = _file(spec)
            for relative in folder_files(source):
                copy(f"{source.rstrip('/')}/{relative}", f"{source.rstrip('/')}/{relative}", f"files.{key}")
        elif source in held:
            found.files[key] = {}
            pending[key] = spec
        elif has_file(source):
            found.files[key] = _file(spec)
            copy(source, source, f"files.{key}")
        else:
            by_hand.append(f"files.{key}: no file '{source}' next to the profile: the entry is not converted")
    where = _examples(items, root, copy, found, by_hand, changes)
    for key, spec in pending.items():
        found.files[key] = _file(spec | {"from": where[spec["from"]]})
    found.tiers = _tier_paths(tiers, items)
    return found


def _entries(value: Any) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(value, dict):
        return []
    return [(str(key), dict(spec)) for key, spec in value.items() if isinstance(spec, dict)]


def _page(spec: dict[str, Any]) -> Any:
    return spec["from"] if set(spec) == {"from"} else spec


def _file(spec: dict[str, Any]) -> Any:
    return spec["from"] if set(spec) == {"from"} else spec


def _items(old: Any, tiers: list[Any], has_file: Callable[[str], bool], changes: list[str],
           by_hand: list[str]) -> list[_Item]:
    found: list[_Item] = []
    examples = old.get("examples")
    for name, spec in (examples.items() if isinstance(examples, dict) else ()):
        found.append(_Item(f"examples.{name}", str(spec.get("path", "")).strip("/"), str(spec.get("file", "")),
                           str(spec.get("note", "")), True))
    for tier in tiers:
        label = f"tiers.{tier.get('name')}"
        if isinstance(tier.get("example"), dict):
            found.append(_tier_item(tier["example"], f"{label}.example", changes))
        for i, helper in enumerate(tier.get("helpers", []) if isinstance(tier.get("helpers"), list) else []):
            found.append(_tier_item(helper, f"{label}.helpers[{i}]", changes))
    kept: list[_Item] = []
    for item in found:
        if not item.path or not item.source:
            by_hand.append(f"{item.label}: no path or no file: the example is not converted")
        elif not has_file(item.source):
            by_hand.append(f"{item.label}: no file '{item.source}' next to the profile: the example is not converted")
        else:
            kept.append(item)
    return kept


def _tier_item(spec: dict[str, Any], label: str, changes: list[str]) -> _Item:
    raw = str(spec.get("note", ""))
    note = plain_note(raw, label, changes) if raw.strip() else ""
    return _Item(label, str(spec.get("path", "")).strip("/"), str(spec.get("file", "")), note, False)


def _sources(old: Any, held: set[str], has_file: Callable[[str], bool],
             folder_files: Callable[[str], tuple[str, ...]], by_hand: list[str]) -> set[str]:
    """The files the profile names that are not examples, by the path they keep."""
    found: set[str] = set()
    for key, spec in _entries(old.get("docs")):
        if "from" in spec and has_file(spec["from"]):
            found.add(spec["from"])
    for key, spec in _entries(old.get("files")):
        source = spec.get("from", "")
        if key.endswith("/"):
            found |= {f"{source.rstrip('/')}/{relative}" for relative in folder_files(source)}
        elif source not in held and has_file(source):
            found.add(source)
    return found


def _root(taken: set[str]) -> str:
    n = 0
    while True:
        name = ROOT if n == 0 else f"{ROOT}-{n}"
        if not any(path == name or path.startswith(name + "/") for path in taken):
            return name
        n += 1


def _examples(items: list[_Item], root: str, copy: Callable[..., bool], found: Gathered, by_hand: list[str],
              changes: list[str]) -> dict[str, str]:
    """Copies each example to its path below the root; returns where each source went."""
    owners: dict[str, str] = {}
    where: dict[str, str] = {}
    for item in items:
        if owners.get(item.path, item.source) != item.source:
            by_hand.append(f"{item.label}: path '{item.path}' is also the path of '{owners[item.path]}': an example is "
                           "named by its path in format 2, so only the first is converted")
            continue
        owners[item.path] = item.source
        copy(f"{root}/{item.path}", item.source, item.label)
        where.setdefault(item.source, f"{root}/{item.path}")
        if item.label.startswith("examples."):
            found.names[item.label.removeprefix("examples.")] = item.path
        if item.note:
            known = found.notes.setdefault(item.path, item.note)
            if known != item.note:
                changes.append(f"{item.label}: the note {item.note!r} is left out: '{item.path}' has the note "
                               f"{known!r}, and format 2 holds one note per path")
    return where


def _tier_paths(tiers: list[Any], items: list[_Item]) -> dict[str, tuple[str | None, list[str]]]:
    kept = {item.label: item.path for item in items}
    found: dict[str, tuple[str | None, list[str]]] = {}
    for tier in tiers:
        label = f"tiers.{tier.get('name')}"
        helpers = [kept[f"{label}.helpers[{i}]"] for i in range(len(tier.get("helpers", []) or []))
                   if f"{label}.helpers[{i}]" in kept]
        found[str(tier.get("name"))] = (kept.get(f"{label}.example"), helpers)
    return found
