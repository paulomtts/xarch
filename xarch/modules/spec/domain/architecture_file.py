"""An architecture file (format version 1), parsed and validated into an Architecture.

The document is what a YAML or JSON parser returned: any value at all. Every problem found is collected, so one
InvalidArchitecture lists them all; a problem that makes the rest meaningless (no mapping, an unknown version)
stops early. The file's keys:

    xarch: 1                   the format version
    name: <name>
    layout: <tree>             a mapping is a folder, `file` a file, {} an empty folder; `each` is the repeating folder, one per instance
                               and needs `singular: <word>` beside it, the name of one instance, as the docs show it
    notes: {<path>: <text>}    optional; the docs' tree note of a folder or file of the layout that is not a part
    parts: {<part>: {path, role, litmus}}     path is a pattern in the layout; `*` stands for the name of an `each` folder
                               a part no tier tests says why with `untested: <reason>`, one line
                               one part may also say `entry: true`: it is the entry point, which drives the rest
    rules: {<part>: [<target>, ...]}          what the part may import: <part>[@own|@any][/<sub path>], or `*`
    layers: {<name>: [<part>, ...]}           optional; chains of parts from the inside out: none imports one after it
    placement: [<part>, ...]                  optional; every part once, in the order its litmus test is run
    naming: [{kind, where, pattern, example}] optional; the docs' naming table, one row per kind of thing
    tiers: [{name, subject, ...}]             optional; the kinds of test, in the order their litmus tests run:
                               name, subject (a list of <part> or <part>/<sub path>), proves, may_touch and
                               litmus (its placement litmus test, lines kept as written) are required; subject_text
                               (the Subject cell as written, instead of the subject's parts; required when the subject
                               is empty), one_file_per, cases_from, data and example ({path, file, note}: its example
                               test, where it would live in a project, the file holding it and a note shown right
                               after its path, as written) and helpers (a list of such files that its tests share,
                               such as builders or a fixture) are optional, and so is types_only (a list of parts its
                               tests may import and use as types, never call: `x: Part` is fine, `Part(...)` is not).
                               With tiers, every part is in some tier's subject or says `untested`, never both
    docs: {<path>: {from, note}}              optional; the project docs `init` writes below docs/project/, in this
                               order: each path is a file, written from the template file `from` (relative to this
                               file) after its placeholders are filled, see docs_template.py; a path ending in `/`
                               is a folder, which takes only a `note` and says how the docs tree shows it. A file
                               has an optional `note`, shown after its line in the tree. A folder holding a single
                               file and no entry of its own is shown on one line, `<file>; <note>`. Without `docs`,
                               `init` writes none
    libraries: {<part>: [<package>, ...]}     optional; the outside packages each part may import, by top-level
                               import name; the standard library is always allowed, and a part not listed may import
                               no outside package. Without `libraries`, outside packages are not checked
    fakes: {path, for, prefix} optional; the folder of the test fakes (path, below the tests root as in tests/fakes)
                               and the parts they stand in for: only a tier whose subject holds one may import them;
                               prefix, optional, is how a fake's name starts (Fake: the fake of DocumentRepo is
                               FakeDocumentRepo), which the guard stand-ins needs
    guards: {<name>: <parameters>}   optional; the pre-built checks in use, each named in GUARDS with its parameters
    examples: {<name>: {part, path, file, note}}   optional; the docs' code examples, each one file of the example
                               project: the part it illustrates, where it would live (path, inside that part and no
                               part nested deeper), the file holding its code and an optional one-line note shown
                               after its path; the docs template shows it by name, see docs_template.py

Files named by docs, examples and the tiers' examples are relative to the architecture file; has_file says whether
one exists. Examples are only ever files: the format takes no inline code.
"""
from __future__ import annotations

import re
import sys
from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import (EACH, EVERYTHING, Architecture, ArchitectureSource, ClosedTree, Doc,
                                              Example, Fakes,
                                              Guard, Layout, NoComments, Naming, PackageOnly, Part, ScenarioCoverage,
                                              Scope, StandIns, Subject, Target, Tier, TierExample)

VERSION = 1
EACH_KEY = "each"
"""How a file writes EACH."""
SINGULAR_KEY = "singular"
"""The key beside `each` naming one instance of it."""
FILE = "file"
"""How a file marks a file in the layout."""

_KEYS = {"xarch", "name", "layout", "notes", "parts", "rules", "layers", "placement", "naming", "tiers", "docs",
         "examples", "libraries", "fakes", "guards"}
_REQUIRED = ("name", "layout", "parts")
_PART_KEYS = {"path", "role", "litmus", "entry", "untested"}
_NAMING_KEYS = {"kind", "where", "pattern", "example"}
_EXAMPLE_KEYS = {"part", "path", "file", "note"}
_DOC_KEYS = {"from", "note"}
_TIER_REQUIRED = ("name", "subject", "proves", "may_touch", "litmus")
_TIER_TEXTS = ("proves", "may_touch", "subject_text", "one_file_per", "cases_from", "data")
"""The keys of a tier that hold one line of text each."""
_TIER_KEYS = {*_TIER_REQUIRED, *_TIER_TEXTS, "example", "helpers", "types_only"}
_TIER_EXAMPLE_KEYS = {"path", "file", "note"}
_PART_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_PACKAGE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
GUARDS = {
    "package-only": "[<part>, ...]: parts that are imported only as a package, never by their files, from outside it",
    "scenario-coverage": "{results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>]}: "
                         "every variant of a union named <Name><suffix> in a results part is the result column of a "
                         "row of the table in its use case's test file of that tier; every row is a pytest.param "
                         "with an id, and a table test has no branching",
    "no-comments": "{}: no `#` comments in the app or its tests; docstrings and tool directives stay",
    "stand-ins": "{}: every Protocol in a part `fakes` stands in for is fire-only (every method returns None) or read "
                 "(any one returns a value), each method annotated; every read port has a fake <prefix><Port> "
                 "under `fakes.path`; and a test of a tier that may import the fakes gives every mock a spec, never "
                 "a read port's",
    "closed-tree": "{}: every Python file of the app lies in a part or is the package file of a folder of the layout; "
                   "off unless switched on, since a profile is a protocol, not a closed world",
}
"""The pre-built checks a file may switch on in `guards`, each with the parameters it takes."""

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
    singular: list[str] = []
    layout = _layout(document.get("layout", {}), "layout", problems, singular)
    if _count_each(layout) > 1:
        problems.append(f"layout: `{EACH_KEY}` may appear only once")
    parts, declared = _parts(document.get("parts", {}), layout, problems)
    notes = _notes(document.get("notes", {}), layout, parts, problems)
    rules = _rules(document.get("rules", {}), parts, declared, problems)
    layers = _layers(document.get("layers", {}), parts, declared, rules, problems)
    placement = _placement(document.get("placement"), parts, declared, problems) if "placement" in document else ()
    naming = _naming(document.get("naming", []), problems)
    tiers = _tiers(document.get("tiers"), parts, declared, has_file, problems) if "tiers" in document else ()
    docs = _docs(document.get("docs", {}), has_file, problems)
    examples = _examples(document.get("examples", {}), parts, declared, layout, has_file, problems)
    libraries = _libraries(document["libraries"], parts, declared, problems) if "libraries" in document else None
    fakes = _fakes(document["fakes"], parts, declared, problems) if "fakes" in document else None
    guards = _guards(document.get("guards", {}), parts, declared, tiers, fakes, problems)
    if problems:
        raise InvalidArchitecture(source, problems)
    return Architecture(name, layout, parts, rules, docs, examples, notes, layers, placement, naming, tiers,
                        libraries, guards, fakes, singular[0] if singular else "")


def _check_version(document: Mapping[Any, Any], source: str) -> None:
    if "xarch" not in document:
        raise InvalidArchitecture(source, [f"missing format version: start the file with `xarch: {VERSION}`"])
    version = document["xarch"]
    if type(version) is not int or version != VERSION:
        raise InvalidArchitecture(source, [f"unknown format version {version!r}: this xarch reads `xarch: {VERSION}`"])


def _layout(value: Any, where: str, problems: list[str], singular: list[str]) -> Layout:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping of folder and file names")
        return {}
    tree: Layout = {}
    has_each = EACH_KEY in value
    if has_each:
        _singular(value, where, problems, singular)
    for key, sub in value.items():
        if has_each and key == SINGULAR_KEY:
            continue
        if not _text(key) or "/" in key or EACH in key or key in (".", ".."):
            problems.append(f"{where}: {key!r} is not a folder or file name")
            continue
        name = EACH if key == EACH_KEY else key
        if sub == FILE and name != EACH:
            tree[name] = None
        elif isinstance(sub, Mapping):
            tree[name] = _layout(sub, f"{where}.{key}", problems, singular)
        else:
            what = "a mapping of what every `each` folder holds" if name == EACH else "a folder (a mapping, {} if empty) or `file`"
            problems.append(f"{where}.{key}: must be {what}, not {sub!r}")
    return tree


def _singular(folder: Mapping[Any, Any], where: str, problems: list[str], singular: list[str]) -> None:
    if SINGULAR_KEY not in folder:
        problems.append(f"{where}: `{EACH_KEY}` needs `{SINGULAR_KEY}` beside it, the name of one instance of the folder")
        return
    value = folder[SINGULAR_KEY]
    if isinstance(value, str) and _PART_NAME.fullmatch(value):
        singular.append(value)
    else:
        problems.append(f"{where}.{SINGULAR_KEY}: must be one word naming an instance of the `{EACH_KEY}` folder, "
                        f"not {value!r}")


def _count_each(tree: Layout) -> int:
    return sum((name == EACH) + (_count_each(sub) if sub else 0) for name, sub in tree.items())


def _parts(value: Any, layout: Layout, problems: list[str]) -> tuple[dict[str, Part], set[str]]:
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
        for key in ("role", "litmus"):
            if key in spec and not isinstance(spec[key], str):
                problems.append(f"{where}.{key}: must be a string")
        if "untested" in spec and not _line(spec["untested"]):
            problems.append(f"{where}.untested: must be one line of text: why no tier tests the part")
        entry = spec.get("entry", False)
        if not isinstance(entry, bool):
            problems.append(f"{where}.entry: must be true or false")
            entry = False
        if entry:
            entries.append(name)
        path = _layout_path(spec.get("path"), layout, f"{where}.path", problems) if "path" in spec else None
        if path is None:
            continue
        if path in claimed:
            problems.append(f"{where}.path: '{'/'.join(path)}' is already claimed by part '{claimed[path]}'")
            continue
        claimed[path] = name
        parts[name] = Part(name, path, _string(spec.get("role")), _string(spec.get("litmus")), entry,
                           spec["untested"] if _line(spec.get("untested")) else "")
    if len(entries) > 1:
        problems.append(f"parts: only one part may be the entry point, not {_quoted(entries)}")
    return parts, declared


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
        problems.append("notes: must be a mapping of layout paths to one line of text, such as {src/shared: ...}")
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
    """A path in the layout, such as 'src/*/api'; problems are reported at `at`."""
    if not _text(value):
        problems.append(f"{at}: must be a path such as 'src/*/api'")
        return None
    path = tuple(value.strip("/").split("/"))
    if path.count(EACH) > 1 or any(EACH in step and step != EACH for step in path):
        problems.append(f"{at}: '{value}' may hold one `*`, standing alone for the name of an `each` folder")
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
            problems.append(f"{where}: must be a list of targets such as [api@own, shared]")
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
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': use @own (the importer's own `each` "
                        "folder) or @any (any `each` folder)")
        return None
    if part.in_instance and scope is None:
        problems.append(f"{where}: {value!r} lies in the `each` folder: say {name}@own or {name}@any")
        return None
    if not part.in_instance and scope is not None:
        problems.append(f"{where}: {value!r} does not lie in the `each` folder: drop '@{scope}'")
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


def _docs(value: Any, has_file: Callable[[str], bool], problems: list[str]) -> tuple[Doc, ...]:
    """The project docs: files with the template each is filled from, and folders with a note."""
    if not isinstance(value, Mapping):
        problems.append("docs: must be a mapping of paths to {from, note}, such as {statement.md: {from: docs/statement.md}}")
        return ()
    docs: list[Doc] = []
    files: set[tuple[str, ...]] = set()
    folders: set[tuple[str, ...]] = set()
    for key, spec in value.items():
        where = f"docs.{key}"
        folder = isinstance(key, str) and key.endswith("/")
        steps = tuple(key.removesuffix("/").split("/")) if isinstance(key, str) else ()
        if not steps or any(step in ("", ".", "..") or "\\" in step for step in steps):
            problems.append(f"{where}: must be a path of plain names below the docs folder")
            continue
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping such as {{from: <file>, note: <text>}}")
            continue
        count = len(problems)
        problems += _unknown_keys(spec, _DOC_KEYS, where)
        if "note" in spec and not _line(spec["note"]):
            problems.append(f"{where}.note: must be one line of text")
        source = _doc_source(spec, where, folder, has_file, problems)
        if len(problems) == count:
            docs.append(Doc(steps, source, spec.get("note", "")))
            (folders if folder else files).add(steps)
    for doc in docs:
        problems += _doc_clashes(doc, files, folders)
    return tuple(docs)


def _doc_source(spec: Mapping[Any, Any], where: str, folder: bool, has_file: Callable[[str], bool],
                problems: list[str]) -> str | None:
    if folder:
        if "from" in spec:
            problems.append(f"{where}: a folder takes only `note`")
        return None
    if "from" not in spec:
        problems.append(f"{where}: missing `from`, the template file")
    elif not _text(spec["from"]):
        problems.append(f"{where}.from: must be a file name")
    elif not has_file(spec["from"]):
        problems.append(f"{where}.from: no file '{spec['from']}' next to the architecture file")
    else:
        return spec["from"]
    return None


def _doc_clashes(doc: Doc, files: set[tuple[str, ...]], folders: set[tuple[str, ...]]) -> list[str]:
    where = f"docs.{'/'.join(doc.path)}{'/' if doc.is_folder else ''}"
    found = [f"{where}: '{'/'.join(doc.path[:i])}' is a file, not a folder"
             for i in range(1, len(doc.path)) if doc.path[:i] in files]
    if doc.is_folder and not any(f[:len(doc.path)] == doc.path and len(f) > len(doc.path) for f in files):
        found.append(f"{where}: holds no file")
    return found


def _tiers(value: Any, parts: dict[str, Part], declared: set[str], has_file: Callable[[str], bool],
           problems: list[str]) -> tuple[Tier, ...]:
    """The tiers, then the coverage: every part is in some tier's subject or is marked untested, and not both.

    Part -> the first tier whose subject names it.
    """
    if not isinstance(value, list) or not value:
        problems.append("tiers: must be a list of tiers such as {name, subject, proves, may_touch, litmus}, "
                        "in the order their litmus tests run")
        return ()
    tiers: list[Tier] = []
    names: set[str] = set()
    claimed: dict[str, str] = {}
    for i, spec in enumerate(value):
        where = f"tiers[{i}]"
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `name`, `subject`, `proves`, `may_touch` and `litmus`")
            continue
        count = len(problems)
        problems += _unknown_keys(spec, _TIER_KEYS, where)
        problems += [f"{where}: missing `{key}`" for key in _TIER_REQUIRED if key not in spec]
        name = spec.get("name")
        if "name" in spec and not _line(name):
            problems.append(f"{where}.name: must be one line of text, such as 'unit'")
        elif name in names:
            problems.append(f"{where}: tier '{name}' is listed twice")
        elif "name" in spec:
            names.add(name)
        problems += [f"{where}.{key}: must be one line of text" for key in _TIER_TEXTS
                     if key in spec and not _line(spec[key])]
        if "litmus" in spec and not _text(spec["litmus"]):
            problems.append(f"{where}.litmus: must be text: the question that tells a test belongs to the tier")
        subject = _subject(spec["subject"], parts, declared, f"{where}.subject", problems) if "subject" in spec else ()
        if "subject" in spec and not spec["subject"] and "subject_text" not in spec:
            problems.append(f"{where}: a subject with no part needs `subject_text`, such as 'the source tree'")
        example = _tier_example(spec["example"], has_file, f"{where}.example", problems) if "example" in spec else None
        helpers = _tier_helpers(spec["helpers"], has_file, f"{where}.helpers", problems) if "helpers" in spec else ()
        types_only = (tuple(_part_names(spec["types_only"], declared, f"{where}.types_only", problems))
                      if "types_only" in spec else ())
        for item in subject:
            claimed.setdefault(item.part, name if _line(name) else where)
        if len(problems) == count:
            tiers.append(Tier(name, subject, spec["proves"], spec["may_touch"], spec["litmus"].strip("\n"),
                              spec.get("subject_text", ""), spec.get("one_file_per", ""), spec.get("cases_from", ""),
                              spec.get("data", ""), example, helpers, tuple(p for p in types_only if p in parts)))
    for part in parts.values():
        if part.untested and part.name in claimed:
            problems.append(f"tiers: part '{part.name}' is in the subject of tier '{claimed[part.name]}' "
                            "and is marked `untested`: drop one")
        elif not part.untested and part.name not in claimed:
            problems.append(f"tiers: no tier tests part '{part.name}': add it to a tier's subject, "
                            "or give the part `untested: <reason>`")
    return tuple(tiers)


def _subject(value: Any, parts: dict[str, Part], declared: set[str], where: str,
             problems: list[str]) -> tuple[Subject, ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of parts, each optionally followed by /<path>, "
                        "such as [api, shared/text]")
        return ()
    subject: list[Subject] = []
    for item in value:
        name, _, sub = item.partition("/") if isinstance(item, str) else ("", "", "")
        steps = tuple(sub.split("/")) if sub else ()
        if not name or name not in declared:
            problems.append(f"{where}: no part named {(name or item)!r}")
        elif any(step in ("", ".", "..") or EACH in step for step in steps) or item.endswith("/"):
            problems.append(f"{where}: {item!r} has an invalid path after the part")
        elif name in parts:
            subject.append(Subject(name, steps))
    return tuple(subject)


def _tier_example(value: Any, has_file: Callable[[str], bool], where: str, problems: list[str]) -> TierExample | None:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping with `path` and `file`, and optionally `note`")
        return None
    count = len(problems)
    problems += _unknown_keys(value, _TIER_EXAMPLE_KEYS, where)
    problems += [f"{where}: missing `{key}`" for key in ("path", "file") if key not in value]
    path = value.get("path")
    steps = tuple(path.strip("/").split("/")) if _text(path) else None
    if "path" in value and (steps is None or any(s in ("", ".", "..") or EACH in s for s in steps)):
        problems.append(f"{where}.path: must be a path such as 'tests/src/billing/api/test_invoice.py'")
    if "file" in value:
        _file(value["file"], has_file, f"{where}.file", problems)
    if "note" in value and not _line(value["note"]):
        problems.append(f"{where}.note: must be one line of text")
    if len(problems) != count or steps is None:
        return None
    return TierExample(steps, value["file"], value.get("note", ""))


def _tier_helpers(value: Any, has_file: Callable[[str], bool], where: str,
                  problems: list[str]) -> tuple[TierExample, ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of files such as {{path, file}}")
        return ()
    helpers = [_tier_example(item, has_file, f"{where}[{i}]", problems) for i, item in enumerate(value)]
    return tuple(helper for helper in helpers if helper is not None)


def _libraries(value: Any, parts: dict[str, Part], declared: set[str],
               problems: list[str]) -> dict[str, tuple[str, ...]]:
    """Every part's outside packages: the listed parts in the file's order, then the others, with none."""
    libraries: dict[str, tuple[str, ...]] = {}
    if not isinstance(value, Mapping):
        problems.append("libraries: must be a mapping of part names to lists of top-level import names")
        return {name: () for name in parts}
    for name, packages in value.items():
        where = f"libraries.{name}"
        if name not in declared:
            problems.append(f"{where}: no part named {name!r}")
            continue
        if not isinstance(packages, list):
            problems.append(f"{where}: must be a list of top-level import names, such as [sqlmodel]")
            continue
        found: list[str] = []
        for package in packages:
            if not isinstance(package, str) or not _PACKAGE.fullmatch(package):
                problems.append(f"{where}: {package!r} is not a top-level import name, such as sqlmodel")
            elif package in sys.stdlib_module_names:
                problems.append(f"{where}: {package!r} is in the standard library, which every part may import")
            elif package in found:
                problems.append(f"{where}: {package!r} is listed twice")
            else:
                found.append(package)
        if name in parts:
            libraries[name] = tuple(found)
    return libraries | {name: () for name in parts if name not in libraries}


def _fakes(value: Any, parts: dict[str, Part], declared: set[str], problems: list[str]) -> Fakes | None:
    where = "fakes"
    if not isinstance(value, Mapping) or not {"path", "for"} <= set(value) <= {"path", "for", "prefix"}:
        problems.append(f"{where}: must be a mapping {{path, for}} and optionally prefix: the folder of the fakes, "
                        "such as tests/fakes, the parts they stand in for, and how a fake's name starts")
        return None
    prefix = value.get("prefix", "")
    if "prefix" in value and (not isinstance(prefix, str) or not _PACKAGE.fullmatch(prefix)):
        problems.append(f"{where}.prefix: must be the start of a class name, such as Fake")
        return None
    path = value["path"]
    steps = tuple(path.strip("/").split("/")) if _text(path) else ()
    if len(steps) < 2 or any(s in ("", ".", "..") or EACH in s for s in steps):
        problems.append(f"{where}.path: must be a folder below the tests root, such as tests/fakes")
        return None
    names = _part_names(value["for"], declared, f"{where}.for", problems)
    return Fakes(steps, tuple(n for n in names if n in parts), prefix)


def _part_names(value: Any, declared: set[str], where: str, problems: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of part names")
        return []
    found: list[str] = []
    for name in value:
        if not isinstance(name, str) or name not in declared:
            problems.append(f"{where}: no part named {name!r}")
        elif name in found:
            problems.append(f"{where}: {name!r} is listed twice")
        else:
            found.append(name)
    return found


def _guards(value: Any, parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...], fakes: Fakes | None,
            problems: list[str]) -> tuple[Guard, ...]:
    if not isinstance(value, Mapping):
        problems.append("guards: must be a mapping of guard names to their parameters, such as {no-comments: {}}")
        return ()
    guards: list[Guard] = []
    for name, spec in value.items():
        where = f"guards.{name}"
        if name not in GUARDS:
            problems.append(f"guards: unknown guard {name!r}: use {', '.join(GUARDS)}")
        elif name == "package-only":
            names = _part_names(spec, declared, where, problems)
            guards.append(PackageOnly(tuple(n for n in names if n in parts)))
        elif name == "scenario-coverage":
            guard = _scenario_coverage(spec, parts, declared, tiers, where, problems)
            if guard is not None:
                guards.append(guard)
        elif spec not in ({}, None):
            problems.append(f"{where}: takes no parameters: write {{}}")
        elif name == "closed-tree":
            guards.append(ClosedTree())
        elif name == "stand-ins":
            if fakes is None or not fakes.prefix:
                problems.append(f"{where}: needs `fakes` with a `prefix`, such as {{path: tests/fakes, for: [<part>], "
                                "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and "
                                "how a fake is named")
            else:
                guards.append(StandIns())
        else:
            guards.append(NoComments())
    return tuple(guards)


def _scenario_coverage(spec: Any, parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...], where: str,
                       problems: list[str]) -> ScenarioCoverage | None:
    keys = {"results", "tier", "suffix", "columns"}
    if not isinstance(spec, Mapping) or set(spec) != keys:
        problems.append(f"{where}: must be a mapping {{results, tier, suffix, columns}}: the part holding the result "
                        "unions, the tier whose test files hold their tables, how a union's name ends, and the three "
                        "names of a table's parameters: its state, its command and its result")
        return None
    count = len(problems)
    results, tier, suffix = spec["results"], spec["tier"], spec["suffix"]
    part = parts.get(results) if isinstance(results, str) else None
    if part is None:
        if not isinstance(results, str) or results not in declared:
            problems.append(f"{where}.results: no part named {results!r}")
    elif not part.in_instance:
        problems.append(f"{where}.results: part '{results}' does not lie in the `each` folder: its unions are "
                        "matched to the tests of the same folder")
    found = next((t for t in tiers if t.name == tier), None)
    if found is None:
        problems.append(f"{where}.tier: no tier named {tier!r}")
    elif part is not None and not any(item.part == results for item in found.subject):
        problems.append(f"{where}.tier: tier '{tier}' does not test part '{results}'")
    if not isinstance(suffix, str) or not _PACKAGE.fullmatch(suffix):
        problems.append(f"{where}.suffix: must be the end of a name, such as Result")
    columns = _columns(spec["columns"], f"{where}.columns", problems)
    return ScenarioCoverage(results, tier, suffix, columns) if len(problems) == count and columns else None


def _columns(value: Any, where: str, problems: list[str]) -> tuple[str, str, str] | None:
    if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, str) for v in value):
        problems.append(f"{where}: must be a list of three names, such as [given, when, then]")
        return None
    count = len(problems)
    for i, name in enumerate(value):
        if not name.isidentifier():
            problems.append(f"{where}: {name!r} is not a name a parameter can have")
        elif name in value[:i]:
            problems.append(f"{where}: {name!r} is listed twice")
    return (value[0], value[1], value[2]) if len(problems) == count else None


def _examples(value: Any, parts: dict[str, Part], declared: set[str], layout: Layout,
              has_file: Callable[[str], bool], problems: list[str]) -> dict[str, Example]:
    if not isinstance(value, Mapping):
        problems.append("examples: must be a mapping of example names to {part, path, file}")
        return {}
    examples: dict[str, Example] = {}
    for name, spec in value.items():
        where = f"examples.{name}"
        if not _text(name) or not _PART_NAME.fullmatch(name):
            problems.append(f"examples: {name!r} is not an example name: use letters, digits, '_' and '-'")
            continue
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `part`, `path` and `file`, and optionally `note`")
            continue
        count = len(problems)
        problems += _unknown_keys(spec, _EXAMPLE_KEYS, where)
        problems += [f"{where}: missing `{key}`" for key in ("part", "path", "file") if key not in spec]
        part_name, path, file, note = spec.get("part"), spec.get("path"), spec.get("file"), spec.get("note", "")
        part = parts.get(part_name) if isinstance(part_name, str) else None
        if "part" in spec and part is None and (not isinstance(part_name, str) or part_name not in declared):
            problems.append(f"{where}.part: no part named {part_name!r}")
        steps = tuple(path.strip("/").split("/")) if _text(path) else None
        if "path" in spec and (steps is None or any(s in ("", ".", "..") or EACH in s for s in steps)):
            problems.append(f"{where}.path: must be a path such as 'src/billing/service/charge.py'")
        elif steps is not None and part is not None:
            problems += _example_path(where, path, steps, part, parts, layout)
        if "file" in spec:
            _file(file, has_file, f"{where}.file", problems)
        if "note" in spec and (not _text(note) or "\n" in note):
            problems.append(f"{where}.note: must be one line of text")
        if len(problems) == count and part is not None and steps is not None:
            examples[name] = Example(name, part.name, steps, file, note)
    return examples


def _example_path(where: str, path: str, steps: tuple[str, ...], part: Part, parts: dict[str, Part],
                  layout: Layout) -> list[str]:
    """An example lies inside its part, and in no part nested deeper inside it."""
    if not _inside(steps, part.path):
        return [f"{where}.path: '{path}' is not inside part '{part.name}' ({'/'.join(part.path)})"]
    claimed = Architecture("", layout, parts, {}).place_of(steps).part
    if claimed != part.name:
        return [f"{where}.path: '{path}' is inside part '{claimed}' ({'/'.join(parts[claimed].path)}), "
                f"which lies within part '{part.name}'"]
    return []


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


def _line(value: Any) -> bool:
    return _text(value) and "\n" not in value


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
