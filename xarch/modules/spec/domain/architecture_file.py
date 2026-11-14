"""An architecture file (format version 1), parsed and validated into an Architecture.

The document is what a YAML or JSON parser returned: any value at all. Every problem found is collected, so one
InvalidArchitecture lists them all; a problem that makes the rest meaningless (no mapping, an unknown version)
stops early. The file's keys:

    xarch: 1                   the format version
    name: <name>
    layout: <tree>             a mapping is a folder, `file` a file, {} an empty folder; `each` is every module's folder
    notes: {<path>: <text>}    optional; the docs' tree note of a folder or file of the layout that is not a part
    parts: {<part>: {path, role, litmus}}     path is a pattern in the layout; `*` stands for the module's name
                               one part may also say `entry: true`: it is the entry point, which drives the modules,
                               and it alone may say `driver_proves: <text>` and `driver_test: {file: <file>}`
    rules: {<part>: [<target>, ...]}          what the part may import: <part>[@own|@any][/<sub path>], or `*`
    layers: {<name>: [<part>, ...]}           optional; chains of parts from the inside out: none imports one after it
    placement: [<part>, ...]                  optional; every part once, in the order its litmus test is run
    naming: [{kind, where, pattern, example}] optional; the docs' naming table, one row per kind of thing
    docs: {template: <file>}                  optional; the architecture.md template, see docs_template.py
    examples: {<part>: {path, file}}          optional; file holds the example's code

Files named by docs.template, driver_test and examples are relative to the architecture file; has_file says whether
one exists.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import (EACH, EVERYTHING, Architecture, ArchitectureSource, Example, Layout,
                                              Naming, Part, Scope, Target)

VERSION = 1
EACH_KEY = "each"                  # how a file writes EACH
FILE = "file"                      # how a file marks a file in the layout

_KEYS = {"xarch", "name", "layout", "notes", "parts", "rules", "layers", "placement", "naming", "docs", "examples"}
_REQUIRED = ("name", "layout", "parts")
_PART_KEYS = {"path", "role", "litmus", "entry", "driver_proves", "driver_test"}
_ENTRY_KEYS = ("driver_proves", "driver_test")     # only on the entry point
_DRIVER_TEST_KEYS = {"file"}
_NAMING_KEYS = {"kind", "where", "pattern", "example"}
_EXAMPLE_KEYS = {"path", "file"}
_DOCS_KEYS = {"template"}
_PART_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_TARGET = re.compile(r"(?P<part>[^@/]*)(?:@(?P<scope>[^/]*))?(?:/(?P<sub>.*))?")


def parse_architecture(document: Any, source: str, has_file: Callable[[str], bool]) -> Architecture:
    """The architecture the document describes; raises InvalidArchitecture listing every problem."""
    problems: list[str] = []
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys, starting with `xarch: 1`"])
    _check_version(document, source)
    unknown = sorted(str(k) for k in document if k not in _KEYS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {_quoted(unknown)}: "
                        f"use {', '.join(sorted(_KEYS))}")
    problems += [f"missing `{key}`" for key in _REQUIRED if key not in document]

    name = document.get("name")
    if "name" in document and not _text(name):
        problems.append("`name` must be a non-empty string")
    layout = _layout(document.get("layout", {}), "layout", problems)
    if _count_each(layout) > 1:
        problems.append(f"layout: `{EACH_KEY}` may appear only once")
    parts, declared = _parts(document.get("parts", {}), layout, has_file, problems)
    notes = _notes(document.get("notes", {}), layout, parts, problems)
    rules = _rules(document.get("rules", {}), parts, declared, problems)
    layers = _layers(document.get("layers", {}), parts, declared, rules, problems)
    placement = _placement(document.get("placement"), parts, declared, problems) if "placement" in document else ()
    naming = _naming(document.get("naming", []), problems)
    template = _docs(document.get("docs", {}), has_file, problems)
    examples = _examples(document.get("examples", {}), parts, declared, has_file, problems)
    if problems:
        raise InvalidArchitecture(source, problems)
    return Architecture(name, layout, parts, rules, template, examples, notes, layers, placement, naming)


def _check_version(document: Mapping[Any, Any], source: str) -> None:
    if "xarch" not in document:
        raise InvalidArchitecture(source, [f"missing format version: start the file with `xarch: {VERSION}`"])
    version = document["xarch"]
    if type(version) is not int or version != VERSION:
        raise InvalidArchitecture(source, [f"unknown format version {version!r}: this xarch reads `xarch: {VERSION}`"])


def _layout(value: Any, where: str, problems: list[str]) -> Layout:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping of folder and file names")
        return {}
    tree: Layout = {}
    for key, sub in value.items():
        if not _text(key) or "/" in key or EACH in key or key in (".", ".."):
            problems.append(f"{where}: {key!r} is not a folder or file name")
            continue
        name = EACH if key == EACH_KEY else key
        if sub == FILE and name != EACH:
            tree[name] = None
        elif isinstance(sub, Mapping):
            tree[name] = _layout(sub, f"{where}.{key}", problems)
        else:
            what = "a mapping of what every module holds" if name == EACH else "a folder (a mapping, {} if empty) or `file`"
            problems.append(f"{where}.{key}: must be {what}, not {sub!r}")
    return tree


def _count_each(tree: Layout) -> int:
    return sum((name == EACH) + (_count_each(sub) if sub else 0) for name, sub in tree.items())


def _parts(value: Any, layout: Layout, has_file: Callable[[str], bool],
           problems: list[str]) -> tuple[dict[str, Part], set[str]]:
    """The valid parts, and the names of every part declared: a part already reported is not reported again."""
    if not isinstance(value, Mapping):
        problems.append("parts: must be a mapping of part names to {path, role, litmus}")
        return {}, set()
    parts: dict[str, Part] = {}
    declared: set[str] = set()
    claimed: dict[tuple[str, ...], str] = {}
    entries: list[str] = []
    for name, spec in value.items():
        where = f"parts.{name}"
        if not _text(name) or not _PART_NAME.fullmatch(name):
            problems.append(f"parts: {name!r} is not a part name: use letters, digits, '_' and '-'")
            continue
        declared.add(name)
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `path` and `role`, and optionally `litmus`")
            continue
        problems += _unknown_keys(spec, _PART_KEYS, where)
        problems += [f"{where}: missing `{key}`" for key in ("path", "role") if key not in spec]
        for key in ("role", "litmus", "driver_proves"):
            if key in spec and not isinstance(spec[key], str):
                problems.append(f"{where}.{key}: must be a string")
        entry = spec.get("entry", False)
        if not isinstance(entry, bool):
            problems.append(f"{where}.entry: must be true or false")
            entry = False
        if entry:
            entries.append(name)
        else:
            problems += [f"{where}.{key}: only the entry point (`entry: true`) has a driver"
                         for key in _ENTRY_KEYS if key in spec]
        driver_test = _driver_test(spec["driver_test"], has_file, where, problems) if "driver_test" in spec else None
        path = _layout_path(spec.get("path"), layout, f"{where}.path", problems) if "path" in spec else None
        if path is None:
            continue
        if path in claimed:
            problems.append(f"{where}.path: '{'/'.join(path)}' is already claimed by part '{claimed[path]}'")
            continue
        claimed[path] = name
        parts[name] = Part(name, path, _string(spec.get("role")), _string(spec.get("litmus")), entry,
                           _string(spec.get("driver_proves")), driver_test)
    if len(entries) > 1:
        problems.append(f"parts: only one part may be the entry point, not {_quoted(entries)}")
    return parts, declared


def _driver_test(value: Any, has_file: Callable[[str], bool], where: str, problems: list[str]) -> str | None:
    where = f"{where}.driver_test"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping such as {{file: examples/driver.py}}")
        return None
    problems += _unknown_keys(value, _DRIVER_TEST_KEYS, where)
    if "file" not in value:
        problems.append(f"{where}: missing `file`")
        return None
    return _file(value["file"], has_file, f"{where}.file", problems)


def _file(value: Any, has_file: Callable[[str], bool], where: str, problems: list[str]) -> str | None:
    if not _text(value):
        problems.append(f"{where}: must be a file name")
        return None
    if not has_file(value):
        problems.append(f"{where}: no file '{value}' next to the architecture file")
        return None
    return value


def _notes(value: Any, layout: Layout, parts: dict[str, Part], problems: list[str]) -> dict[tuple[str, ...], str]:
    if not isinstance(value, Mapping):
        problems.append("notes: must be a mapping of layout paths to one line of text, such as {kernel/logic: ...}")
        return {}
    owners = {part.path: name for name, part in parts.items()}
    notes: dict[tuple[str, ...], str] = {}
    for key, text in value.items():
        where = f"notes.{key}"
        path = _layout_path(key, layout, where if _text(key) else f"notes: {key!r}", problems)
        if path is None:
            continue
        if path in owners:
            problems.append(f"{where}: '{key}' is part '{owners[path]}', whose note is its role")
            continue
        if not _text(text) or "\n" in text:
            problems.append(f"{where}: must be one line of text")
            continue
        notes[path] = text
    return notes


def _layout_path(value: Any, layout: Layout, at: str, problems: list[str]) -> tuple[str, ...] | None:
    """A path in the layout, such as 'modules/*/domain'; problems are reported at `at`."""
    if not _text(value):
        problems.append(f"{at}: must be a path such as 'modules/*/domain'")
        return None
    path = tuple(value.strip("/").split("/"))
    if path.count(EACH) > 1 or any(EACH in step and step != EACH for step in path):
        problems.append(f"{at}: '{value}' may hold one `*`, standing alone for the module's name")
        return None
    if not _resolves(path, layout):
        problems.append(f"{at}: '{value}' matches no folder or file in layout"
                        + (f" (`*` matches `{EACH_KEY}`)" if EACH_KEY in path else ""))
        return None
    return path


def _resolves(path: tuple[str, ...], layout: Layout) -> bool:
    here: Layout | None = layout
    for step in path:
        if here is None or step not in here:
            return False
        here = here[step]
    return True


def _rules(value: Any, parts: dict[str, Part], declared: set[str],
           problems: list[str]) -> dict[str, tuple[Target, ...]]:
    rows: dict[str, tuple[Target, ...]] = {name: () for name in parts}
    if not isinstance(value, Mapping):
        problems.append("rules: must be a mapping of part names to lists of targets")
        return rows
    for name, targets in value.items():
        where = f"rules.{name}"
        if name not in declared:
            problems.append(f"{where}: no part named {name!r}")
            continue
        if not isinstance(targets, list):
            problems.append(f"{where}: must be a list of targets such as [domain@own, kernel]")
            continue
        parsed = [_target(t, parts, declared, where, problems) for t in targets]
        rows[name] = tuple(t for t in parsed if t is not None)
    return rows


def _target(value: Any, parts: dict[str, Part], declared: set[str], where: str,
            problems: list[str]) -> Target | None:
    if value == EVERYTHING:
        return Target(EVERYTHING)
    match = _TARGET.fullmatch(value) if isinstance(value, str) else None
    if match is None or not match["part"]:
        problems.append(f"{where}: {value!r} is not a target: use <part>, <part>@own, <part>@any, "
                        "optionally followed by /<path>, or *")
        return None
    name, scope, sub = match["part"], match["scope"], match["sub"]
    part = parts.get(name)
    if part is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    if scope is not None and scope not in ("own", "any"):
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': use @own (the importer's module) "
                        "or @any (any module)")
        return None
    if part.in_module and scope is None:
        problems.append(f"{where}: {value!r} is a part of every module: say {name}@own or {name}@any")
        return None
    if not part.in_module and scope is not None:
        problems.append(f"{where}: {value!r} is not a part of a module: drop '@{scope}'")
        return None
    steps = tuple(sub.split("/")) if sub is not None else ()
    if any(not step or step in (".", "..") or EACH in step for step in steps):
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    chosen: Scope = scope if scope is not None else "none"
    return Target(name, chosen, steps)


def _layers(value: Any, parts: dict[str, Part], declared: set[str], rules: dict[str, tuple[Target, ...]],
            problems: list[str]) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        problems.append("layers: must be a mapping of names to lists of parts, from the inside out")
        return {}
    layers: dict[str, tuple[str, ...]] = {}
    seen: dict[str, str] = {}
    for name, chain in value.items():
        where = f"layers.{name}"
        if not _text(name) or not _PART_NAME.fullmatch(name):
            problems.append(f"layers: {name!r} is not a name: use letters, digits, '_' and '-'")
            continue
        if not isinstance(chain, list) or not chain:
            problems.append(f"{where}: must be a list of parts, from the inside out")
            continue
        ok = True
        for part in chain:
            if not isinstance(part, str) or part not in declared:
                problems.append(f"{where}: no part named {part!r}")
                ok = False
            elif part in seen:
                problems.append(f"{where}: part '{part}' is already in layer '{seen[part]}'")
                ok = False
            else:
                seen[part] = name
        if not ok or any(part not in parts for part in chain):
            continue
        for i, inner in enumerate(chain):
            outward = [t.part for t in rules.get(inner, ()) if t.part in chain[i + 1:] and t.part != inner]
            problems += [f"{where}: '{inner}' imports '{outer}', which is outward of it" for outer in outward]
        layers[name] = tuple(chain)
    return layers


def _placement(value: Any, parts: dict[str, Part], declared: set[str], problems: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list):
        problems.append("placement: must be a list of every part, in the order their litmus tests run")
        return ()
    order: list[str] = []
    for part in value:
        if not isinstance(part, str) or part not in declared:
            problems.append(f"placement: no part named {part!r}")
        elif part in order:
            problems.append(f"placement: part '{part}' is listed twice")
        else:
            order.append(part)
    missing = [name for name in parts if name not in order]
    if missing:
        problems.append(f"placement: missing part{'s' if len(missing) > 1 else ''} {_quoted(missing)}: "
                        "list every part once")
    return tuple(order)


def _naming(value: Any, problems: list[str]) -> tuple[Naming, ...]:
    if not isinstance(value, list):
        problems.append("naming: must be a list of rows such as {kind, where, pattern, example}")
        return ()
    rows: list[Naming] = []
    for i, spec in enumerate(value):
        where = f"naming[{i}]"
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `kind`, `where`, `pattern` and `example`")
            continue
        count = len(problems)
        problems += _unknown_keys(spec, _NAMING_KEYS, where)
        problems += [f"{where}: missing `{key}`" for key in ("kind", "where", "pattern", "example") if key not in spec]
        problems += [f"{where}.{key}: must be a string" for key in ("kind", "pattern")
                     if key in spec and not _text(spec[key])]
        lists = {key: _strings(spec.get(key)) for key in ("where", "example")}
        problems += [f"{where}.{key}: must be a string or a list of strings" for key, found in lists.items()
                     if key in spec and found is None]
        if len(problems) == count:
            rows.append(Naming(spec["kind"], lists["where"] or (), spec["pattern"], lists["example"] or ()))
    return tuple(rows)


def _strings(value: Any) -> tuple[str, ...] | None:
    if _text(value):
        return (value,)
    if isinstance(value, list) and value and all(_text(v) for v in value):
        return tuple(value)
    return None


def _docs(value: Any, has_file: Callable[[str], bool], problems: list[str]) -> str | None:
    if not isinstance(value, Mapping):
        problems.append("docs: must be a mapping such as {template: architecture.md}")
        return None
    problems += _unknown_keys(value, _DOCS_KEYS, "docs")
    template = value.get("template")
    if template is None:
        return None
    if not _text(template):
        problems.append("docs.template: must be a file name")
        return None
    if not has_file(template):
        problems.append(f"docs.template: no file '{template}' next to the architecture file")
    return template


def _examples(value: Any, parts: dict[str, Part], declared: set[str], has_file: Callable[[str], bool],
              problems: list[str]) -> dict[str, Example]:
    if not isinstance(value, Mapping):
        problems.append("examples: must be a mapping of part names to {path, file}")
        return {}
    examples: dict[str, Example] = {}
    for name, spec in value.items():
        where = f"examples.{name}"
        part = parts.get(name) if isinstance(name, str) else None
        if part is None:
            if name not in declared:
                problems.append(f"{where}: no part named {name!r}")
            continue
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `path` and `file`")
            continue
        problems += _unknown_keys(spec, _EXAMPLE_KEYS, where)
        problems += [f"{where}: missing `{key}`" for key in ("path", "file") if key not in spec]
        path, file = spec.get("path"), spec.get("file")
        ok = True
        if "path" in spec:
            if not _text(path):
                problems.append(f"{where}.path: must be a path such as 'src/billing/service/charge.py'")
                ok = False
            elif not _inside(tuple(path.strip("/").split("/")), part.path):
                problems.append(f"{where}.path: '{path}' is not inside part '{name}' ({'/'.join(part.path)})")
                ok = False
        if "file" in spec:
            if not _text(file):
                problems.append(f"{where}.file: must be a file name")
                ok = False
            elif not has_file(file):
                problems.append(f"{where}.file: no file '{file}' next to the architecture file")
                ok = False
        if ok and "path" in spec and "file" in spec:
            examples[name] = Example(tuple(path.strip("/").split("/")), file)
    return examples


def _inside(path: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    if len(path) < len(pattern):
        return False
    return all(want == step or (want == EACH and step != EACH) for want, step in zip(pattern, path))


def _unknown_keys(spec: Mapping[Any, Any], known: set[str], where: str) -> list[str]:
    unknown = sorted(str(k) for k in spec if k not in known)
    if not unknown:
        return []
    return [f"{where}: unknown key{'s' if len(unknown) > 1 else ''} {_quoted(unknown)}: use {', '.join(sorted(known))}"]


def _text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _quoted(names: list[str]) -> str:
    return ", ".join(f"'{n}'" for n in names)


def source_of(location: str | Path, bundled: Collection[str]) -> ArchitectureSource:
    """A bare name (no folder, no suffix) is a bundled architecture; anything else is a path to a file."""
    path = Path(location)
    if isinstance(location, Path) or len(path.parts) != 1 or path.suffix:
        return ArchitectureSource(str(location), bundled=False)
    if location not in bundled:
        raise InvalidArchitecture(str(location), [f"no bundled architecture '{location}': use one of "
                                                  f"{', '.join(bundled)}, or a path to a .yaml or .json file"])
    return ArchitectureSource(location, bundled=True)
