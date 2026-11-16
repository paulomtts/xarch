"""The files of a profile in format 1 that a profile in format 2 holds differently: the docs' templates, the files `init`
writes and the examples. Format 2 lists folders of example projects and names an example by its path in the project, so
every example file is copied to that path below one folder, and a template quotes it by the path."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from typing import Any

from xarch.modules.spec.application.logic.profile_listing import listing_in
from xarch.modules.spec.domain.migration import Copy

PLACEHOLDER = re.compile(r"\{\{example:(.*?)\}\}")
ROOT = "examples"


@dataclass(frozen=True)
class Gathered:
    """copies: the files of the converted folder; pages and files: the converted values of `docs` and `files`; names:
    each example's name with its path; notes: each path with its plain note; root: the folder of the examples ("" for
    none); tiers: for each tier, its example's path (or None) and its helpers' paths."""
    copies: tuple[Copy, ...]
    names: Mapping[str, str]
    notes: Mapping[str, str]
    root: str
    pages: Mapping[str, Any]
    files: Mapping[str, Any]
    tiers: Mapping[str, tuple[str | None, list[str]]]


def _copy(copies: list[Copy], by_hand: list[str], destination: str, source: str, label: str,
          rewritten: bool = False) -> None:
    """Add a file to the converted folder, each destination taken by one source: a second source for a taken
    destination is reported in by_hand, not copied."""
    taken = next((copy.source for copy in copies if copy.destination == destination), None)
    if taken is None:
        copies.append(Copy(destination, source, rewritten))
    elif taken != source:
        by_hand.append(f"{label}: '{source}' would be copied to '{destination}', which '{taken}' already takes: give "
                       "one of them another path")


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


def rewritten_template(destination: str, text: str, names: dict[str, str]) -> tuple[str, int, list[str]]:
    """A template of the converted folder at destination: its text with the examples it quotes named by their paths,
    how many of its placeholders were rewritten, and what is left to fix by hand."""
    rewritten, unknown = rewrite_examples(text, names)
    by_hand = [f"{destination}: {{{{example:{name}}}}} names no example: left as written, write the path of the example"
               for name in unknown]
    return rewritten, len(PLACEHOLDER.findall(rewritten)) - len(unknown), by_hand


def plain_note(note: str, label: str, changes: list[str]) -> str:
    """A note of format 1 that was shown right after a path as written: its text without the outer parentheses."""
    text = note.strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    stripped = text.strip(":;,- ").strip()
    changes.append(f"{label}: the note {note!r} was shown after the path as written; format 2 shows it in "
                   f"parentheses as {stripped!r}")
    return stripped


def referenced_v1(document: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The files and the folders a profile in format 1 names next to it, each as written and sorted: the templates of
    `docs`, the files of `files` (a key ending in / names a folder), and the file of each example, helper included.
    What is no mapping or no text is left out."""
    files: set[str] = set()
    folders: set[str] = set()
    if not isinstance(document, dict):
        return (), ()
    files |= {spec["from"] for _, spec in _entries(document.get("docs")) if isinstance(spec.get("from"), str)}
    for key, spec in _entries(document.get("files")):
        (folders if key.endswith("/") else files).add(str(spec.get("from", "")))
    examples = document.get("examples")
    files |= {str(spec.get("file", "")) for spec in (examples.values() if isinstance(examples, dict) else ())
              if isinstance(spec, dict)}
    for tier in document.get("tiers") if isinstance(document.get("tiers"), list) else ():
        if not isinstance(tier, dict):
            continue
        helpers = tier.get("helpers") if isinstance(tier.get("helpers"), list) else []
        files |= {str(spec.get("file", "")) for spec in (tier.get("example"), *helpers) if isinstance(spec, dict)}
    return tuple(sorted(files)), tuple(sorted(folders))


def gather(old: Any, tiers: list[Any], files: Collection[str], changes: list[str], by_hand: list[str]) -> Gathered:
    """Everything the old profile names as a file, converted; files are the files next to it that it names, and every
    file below the folders it names, each as a path from the profile's folder (see referenced_v1)."""
    items = _items(old, tiers, files, changes, by_hand)
    held = {item.source for item in items}
    plain = _sources(old, held, files, by_hand)
    root = _root(plain)
    copies: list[Copy] = []
    pages: dict[str, Any] = {}
    for key, spec in _entries(old.get("docs")):
        source = spec.get("from")
        if source is not None and source not in files:
            by_hand.append(f"docs.{key}: no file '{source}' next to the profile: the page is not converted")
            continue
        pages[key] = _page(spec)
        if source is not None:
            _copy(copies, by_hand, source, source, f"docs.{key}", True)
    pending: dict[str, dict[str, Any]] = {}
    converted: dict[str, Any] = {}
    for key, spec in _entries(old.get("files")):
        source = spec.get("from", "")
        if key.endswith("/"):
            converted[key] = _file(spec)
            for relative in listing_in(files, source) or ():
                _copy(copies, by_hand, f"{source.rstrip('/')}/{relative}", f"{source.rstrip('/')}/{relative}",
                      f"files.{key}")
        elif source in held:
            converted[key] = {}
            pending[key] = spec
        elif source in files:
            converted[key] = _file(spec)
            _copy(copies, by_hand, source, source, f"files.{key}")
        else:
            by_hand.append(f"files.{key}: no file '{source}' next to the profile: the entry is not converted")
    where, names, notes = _examples(items, root, copies, by_hand, changes)
    for key, spec in pending.items():
        converted[key] = _file(spec | {"from": where[spec["from"]]})
    return Gathered(tuple(copies), names, notes, root if items else "", pages, converted, _tier_paths(tiers, items))


def _entries(value: Any) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(value, dict):
        return []
    return [(str(key), dict(spec)) for key, spec in value.items() if isinstance(spec, dict)]


def _page(spec: dict[str, Any]) -> Any:
    return spec["from"] if set(spec) == {"from"} else spec


def _file(spec: dict[str, Any]) -> Any:
    return spec["from"] if set(spec) == {"from"} else spec


def _items(old: Any, tiers: list[Any], files: Collection[str], changes: list[str], by_hand: list[str]) -> list[_Item]:
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
        elif item.source not in files:
            by_hand.append(f"{item.label}: no file '{item.source}' next to the profile: the example is not converted")
        else:
            kept.append(item)
    return kept


def _tier_item(spec: dict[str, Any], label: str, changes: list[str]) -> _Item:
    raw = str(spec.get("note", ""))
    note = plain_note(raw, label, changes) if raw.strip() else ""
    return _Item(label, str(spec.get("path", "")).strip("/"), str(spec.get("file", "")), note, False)


def _sources(old: Any, held: set[str], files: Collection[str], by_hand: list[str]) -> set[str]:
    """The files the profile names that are not examples, by the path they keep."""
    found: set[str] = set()
    for key, spec in _entries(old.get("docs")):
        if "from" in spec and spec["from"] in files:
            found.add(spec["from"])
    for key, spec in _entries(old.get("files")):
        source = spec.get("from", "")
        if key.endswith("/"):
            found |= {f"{source.rstrip('/')}/{relative}" for relative in listing_in(files, source) or ()}
        elif source not in held and source in files:
            found.add(source)
    return found


def _root(taken: set[str]) -> str:
    n = 0
    while True:
        name = ROOT if n == 0 else f"{ROOT}-{n}"
        if not any(path == name or path.startswith(name + "/") for path in taken):
            return name
        n += 1


def _examples(items: list[_Item], root: str, copies: list[Copy], by_hand: list[str],
              changes: list[str]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Copies each example to its path below the root; returns where each source went, each example's name with its
    path, and each path with its note."""
    owners: dict[str, str] = {}
    where: dict[str, str] = {}
    names: dict[str, str] = {}
    notes: dict[str, str] = {}
    for item in items:
        if owners.get(item.path, item.source) != item.source:
            by_hand.append(f"{item.label}: path '{item.path}' is also the path of '{owners[item.path]}': an example is "
                           "named by its path in format 2, so only the first is converted")
            continue
        owners[item.path] = item.source
        _copy(copies, by_hand, f"{root}/{item.path}", item.source, item.label)
        where.setdefault(item.source, f"{root}/{item.path}")
        if item.label.startswith("examples."):
            names[item.label.removeprefix("examples.")] = item.path
        if item.note:
            known = notes.setdefault(item.path, item.note)
            if known != item.note:
                changes.append(f"{item.label}: the note {item.note!r} is left out: '{item.path}' has the note "
                               f"{known!r}, and format 2 holds one note per path")
    return where, names, notes


def _tier_paths(tiers: list[Any], items: list[_Item]) -> dict[str, tuple[str | None, list[str]]]:
    kept = {item.label: item.path for item in items}
    found: dict[str, tuple[str | None, list[str]]] = {}
    for tier in tiers:
        label = f"tiers.{tier.get('name')}"
        helpers = [kept[f"{label}.helpers[{i}]"] for i in range(len(tier.get("helpers", []) or []))
                   if f"{label}.helpers[{i}]" in kept]
        found[str(tier.get("name"))] = (kept.get(f"{label}.example"), helpers)
    return found
