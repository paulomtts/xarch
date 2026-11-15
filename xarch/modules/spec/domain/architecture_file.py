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
                               tests may import and use as types, never call: `x: Part` is fine, `Part(...)` is not),
                               and so is forbidden (true: its tests are held to the `forbidden` list of the part
                               they mirror). With tiers, every part is in some tier's subject or says `untested`,
                               never both
    docs: {<path>: {from, note}}              optional; the project docs `init` writes below docs/project/, in this
                               order: each path is a file, written from the template file `from` (relative to this
                               file) after its placeholders are filled, see docs_template.py; a path ending in `/`
                               is a folder, which takes only a `note` and says how the docs tree shows it. A file
                               has an optional `note`, shown after its line in the tree. A folder holding a single
                               file and no entry of its own is shown on one line, `<file>; <note>`. Without `docs`,
                               `init` writes none
    files: {<path>: {from, pinned, fill}}     optional; the other files `init` writes, in this order, beside the app
                               folder (in the folder holding it, with docs/ and pyproject.toml), or inside it: each
                               path is relative to that folder, e.g. tests/architecture/test_rules.py, and `from`
                               names the template file it is written from (relative to this file). The text is written
                               as it stands, except that `{{app}}`, the name of the app folder, is replaced by it
                               (in a path too, so an entry may land inside the app: {{app}}/web/ui/); any other
                               `{{...}}` stays. A path may not be empty, start with `/`, hold `..` or an empty step,
                               or clash with a doc's path, docs/project/<path>. A path ending in `/` is a folder
                               entry: `from` is a folder (relative to this file) holding at least one file, and
                               every file under it is written below the path, keeping its relative path; entries may
                               not overlap (a file or folder inside a folder entry, the same path twice). `init`,
                               which knows the app folder, also refuses a file that would replace what the skeleton
                               writes inside it (see project_files.py). A file is never overwritten. Without `files`,
                               `init` writes none. pinned (true or false, default false; not for a folder entry):
                               the project keeps the file as `init` writes it, and `check` reports it when it
                               differs from what `init` would write now. fill (true or false; default true for a
                               file, false for a folder): whether `{{app}}` is filled in; off, the bytes are copied
                               unchanged, which a binary file needs; on, a file that is not UTF-8 text is refused
    libraries: {<part>: [<package>, ...]}     optional; the outside packages each part may import, by top-level
                               import name; the standard library is always allowed, and a part not listed may import
                               no outside package. Without `libraries`, outside packages are not checked
    hints: {<rule id>: <text>}                optional; the project's own advice for a rule, one line each, shown after
                               the built-in fix of every violation of that rule, in the text output and in the
                               JSON's `hint`. The rule id is one of RULES in xarch/kernel/violations.py, the `rule` a
                               violation names; any other is refused
    excluded: {<folder>: <reason>}            optional; folders below the app that are not its source (such as example
                               code shipped as data): a path with no `..`, no leading `/` and no `*`, not a folder of
                               the layout, none inside or holding another, each with the one-line reason it is left
                               out. No check reads a Python file below one; `check` lists each in its enforcement
                               section, so the exclusion stays visible
    forbidden: {<part>: [<name>, ...]}        optional; what each part may not use: a dotted name as an absolute import
                               binds it (datetime.datetime.now; a builtin as builtins.open), or a module by its import
                               name (socket); a file of the part may neither import it (or below it) nor use it by
                               name, see the rules module's forbidden check. Each list is non-empty, each name once
    fakes: {path, for, prefix} optional; the folder of the test fakes (path, below the tests root as in tests/fakes)
                               and the parts they stand in for: only a tier whose subject holds one may import them;
                               prefix, optional, is how a fake's name starts (Fake: the fake of DocumentRepo is
                               FakeDocumentRepo), which the guard stand-ins needs
    tests: {files, functions, skips}  how the project's test framework names things: `files` is a list of patterns
                               of a test file's name (a .py name, `*` for any text) and `functions` the pattern of a
                               test function's name; `skips`, optional, the dotted names of what skips a test or
                               expects it to fail (a marker or a call), which `check` counts. Required with `tiers` and with a guard that
                               reads tests
                               (scenario-coverage, stand-ins): they cannot tell a test without it. The names of
                               the framework itself (its decorator, its mocks) are the parameters of those guards;
                               xarch's code holds none of them. Python stays fixed: `typing.Protocol` marks a port,
                               imports and the syntax tree are read as Python defines them
    guards: {<name>: <parameters>}   optional; the pre-built checks in use, each named in GUARDS with its parameters
                               stand-ins may add `fixtures: {<parameter>: {mocks: [<method>, ...], autospec: [<method>, ...]}}`:
                               the parameters of a test function whose methods build a mock, as a fixture hands one
                               over (a call of `<parameter>.<method>` follows the rules of the dotted names in `mocks`
                               and `autospec`); each parameter is a plain name, its `mocks` required and its
                               `autospec` optional, each list of method names non-empty with each name once
    examples: {<name>: {part, path, file, note}}   optional; the docs' code examples, each one file of the example
                               project: the part it illustrates, where it would live (path, inside that part and no
                               part nested deeper), the file holding its code and an optional one-line note shown
                               after its path; the docs template shows it by name, see docs_template.py

Files named by docs, files, examples and the tiers' examples are relative to the architecture file; has_file says whether
one exists. Examples are only ever files: the format takes no inline code.
"""
from __future__ import annotations

import re
import sys
from collections.abc import Callable, Collection, Mapping
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.docs import DOCS_ROOT
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.project_files import APP_PLACEHOLDER
from xarch.modules.spec.domain.values import (
    EACH,
    EVERYTHING,
    NAME,
    Architecture,
    ArchitectureSource,
    CaseTable,
    ClosedTree,
    Doc,
    Example,
    Excluded,
    Fakes,
    Fixture,
    Framework,
    Guard,
    Layout,
    Naming,
    NoComments,
    PackageOnly,
    Part,
    ProjectFile,
    ScenarioCoverage,
    Scope,
    StandIns,
    Subject,
    Target,
    Tier,
    TierExample,
)

VERSION = 1
EACH_KEY = "each"
"""How a file writes EACH."""
SINGULAR_KEY = "singular"
"""The key beside `each` naming one instance of it."""
FILE = "file"
"""How a file marks a file in the layout."""

_KEYS = {"xarch", "name", "layout", "notes", "parts", "rules", "layers", "placement", "naming", "tiers", "docs",
         "files", "examples", "libraries", "fakes", "guards", "tests", "forbidden", "excluded", "hints"}
_REQUIRED = ("name", "layout", "parts")
_PART_KEYS = {"path", "role", "litmus", "entry", "untested"}
_NAMING_KEYS = {"kind", "where", "pattern", "example"}
_EXAMPLE_KEYS = {"part", "path", "file", "note"}
_DOC_KEYS = {"from", "note"}
_FILE_KEYS = {"from", "pinned", "fill"}
_TIER_REQUIRED = ("name", "subject", "proves", "may_touch", "litmus")
_TIER_TEXTS = ("proves", "may_touch", "subject_text", "one_file_per", "cases_from", "data")
"""The keys of a tier that hold one line of text each."""
_TIER_KEYS = {*_TIER_REQUIRED, *_TIER_TEXTS, "example", "helpers", "types_only", "forbidden"}
_TIER_EXAMPLE_KEYS = {"path", "file", "note"}
_PART_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_PACKAGE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_DOTTED = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+")
_NAME_OR_DOTTED = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
_FILE_PATTERN = re.compile(r"[A-Za-z0-9_.*-]+\.py")
_FILE_NAME = re.compile(r"[A-Za-z0-9_.-]+\.py")
_FUNCTION_PATTERN = re.compile(r"[A-Za-z0-9_*]+")
_TESTS_KEYS = {"files", "functions"}
_TESTS_OPTIONAL = {"skips"}
_SCENARIO_KEYS = {"results", "tier", "suffix", "columns", "table", "file"}
_TABLE_KEYS = {"decorator", "row", "id", "keywords"}
_TABLE_REQUIRED = ("decorator", "row", "id")
_STAND_INS_KEYS = {"mocks", "autospec", "spec", "fixtures"}
_FIXTURE_KEYS = {"mocks", "autospec"}
GUARDS = {
    "package-only": "[<part>, ...]: parts that are imported only as a package, never by their files, from outside it",
    "scenario-coverage": "{results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], "
                         "table: {decorator, row, id, keywords}, file: <name>}: every variant of a union named "
                         "<Name><suffix> in a results part is the result column of a row of the table in its use "
                         "case's test file <file> of that tier; every row is a <table.row> call with an <table.id>, "
                         "and a table test has no branching",
    "no-comments": "{}: no `#` comments in the app or its tests; docstrings and tool directives stay",
    "stand-ins": "{mocks: [<dotted name>, ...], autospec: [<dotted name>, ...], spec: [<keyword>, ...], "
                 "fixtures: {<parameter>: {mocks: [<method>, ...], autospec: [<method>, ...]}}}: every "
                 "Protocol in a part `fakes` stands in for is fire-only (every method returns None) or read (any one "
                 "returns a value), each method annotated; every read port has a fake <prefix><Port> under "
                 "`fakes.path`; and a test of a tier that may import the fakes gives every mock a spec, never a "
                 "read port's",
    "closed-tree": "{}: every Python file of the app lies in a part or is the package file of a folder of the layout; "
                   "off unless switched on, since a profile is a protocol, not a closed world",
}
"""The pre-built checks a file may switch on in `guards`, each with the parameters it takes."""
_GUARD_NAMES: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage",
                                 NoComments: "no-comments", StandIns: "stand-ins", ClosedTree: "closed-tree"}


def guard_name(guard: Guard) -> str:
    """The name a file switches the guard on by, one of GUARDS."""
    return _GUARD_NAMES[type(guard)]

_TARGET = re.compile(r"(?P<part>[^@/]*)(?:@(?P<scope>[^/]*))?(?:/(?P<sub>.*))?")


def parse_architecture(document: Any, source: str, has_file: Callable[[str], bool],
                       folder_files: Callable[[str], tuple[str, ...] | None] | None = None) -> Architecture:
    """The architecture the document describes; raises InvalidArchitecture listing every problem. folder_files says
    which files lie under a folder next to the architecture file, None when it is no folder; without it, no folder
    exists."""
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
    files = _files(document.get("files", {}), docs, has_file, folder_files or (lambda relative: None), problems)
    examples = _examples(document.get("examples", {}), parts, declared, layout, has_file, problems)
    libraries = _libraries(document["libraries"], parts, declared, problems) if "libraries" in document else None
    forbidden = _forbidden(document["forbidden"], parts, declared, problems) if "forbidden" in document else {}
    fakes = _fakes(document["fakes"], parts, declared, problems) if "fakes" in document else None
    framework = _framework(document["tests"], problems) if "tests" in document else None
    excluded = _excluded(document["excluded"], layout, problems) if "excluded" in document else ()
    hints = _hints(document["hints"], problems) if "hints" in document else {}
    guards = _guards(document.get("guards", {}), parts, declared, tiers, fakes, framework, problems)
    if "tests" not in document:
        problems += _needs_tests(document, tiers)
    if problems:
        raise InvalidArchitecture(source, problems)
    return Architecture(name, layout, parts, rules, docs, examples, notes, layers, placement, naming, tiers,
                        libraries, guards, fakes, singular[0] if singular else "", files, framework, forbidden, excluded, hints)


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


def _files(value: Any, docs: tuple[Doc, ...], has_file: Callable[[str], bool],
           folder_files: Callable[[str], tuple[str, ...] | None], problems: list[str]) -> tuple[ProjectFile, ...]:
    """The project files: each path below the project root with the template, or the folder, it is written from."""
    if not isinstance(value, Mapping):
        problems.append("files: must be a mapping of paths to {from}, such as {tests/rules.py: {from: guard.py}}")
        return ()
    found: list[ProjectFile] = []
    for key, spec in value.items():
        folder = isinstance(key, str) and key.endswith("/")
        where = f"files.{key}"
        steps = tuple(key.removesuffix("/").split("/")) if isinstance(key, str) else ()
        if not steps or any(step in ("", ".", "..") or "\\" in step for step in steps):
            problems.append(f"{where}: must be a path of plain names below the project root")
            continue
        if re.search(r"[{}]", key.replace(APP_PLACEHOLDER, "")):
            problems.append(f"{where}: must be a path of plain names below the project root; "
                            f"the only placeholder is {APP_PLACEHOLDER}")
            continue
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping such as {{from: <file>}}")
            continue
        count = len(problems)
        problems += _unknown_keys(spec, _FILE_KEYS, where)
        source = (_folder_source(spec, where, has_file, folder_files, problems) if folder
                  else _file_source(spec, where, has_file, folder_files, problems))
        pinned = spec.get("pinned", False)
        if not isinstance(pinned, bool):
            problems.append(f"{where}.pinned: must be true or false: whether `check` reports the file when it differs "
                            "from what `init` writes")
        elif pinned and folder:
            problems.append(f"{where}.pinned: a folder entry cannot be pinned: a project edits what it copies")
        fill = spec.get("fill", not folder)
        if not isinstance(fill, bool):
            problems.append(f"{where}.fill: must be true or false: whether `{APP_PLACEHOLDER}` is filled in")
        if len(problems) == count:
            found.append(ProjectFile(steps, source or "", pinned, folder, fill))
    for file in found:
        problems += _file_clashes(file, found, docs)
    return tuple(found)


def _entry(file: ProjectFile) -> str:
    return "/".join(file.path) + ("/" if file.folder else "")


def _file_clashes(file: ProjectFile, files: list[ProjectFile], docs: tuple[Doc, ...]) -> list[str]:
    where = f"files.{_entry(file)}"
    found = [f"{where}: '{'/'.join(file.path[:i])}' is a file, not a folder"
             for i in range(1, len(file.path)) if any(o.path == file.path[:i] and not o.folder for o in files)]
    for other in files:
        if not other.folder or other is file:
            continue
        if file.path == other.path:
            found.append(f"{where}: is also a folder entry")
        elif file.path[:len(other.path)] == other.path:
            found.append(f"{where}: lies inside the folder entry '{_entry(other)}'")
    for doc in docs:
        written = DOCS_ROOT + doc.path
        if doc.source is not None and (written[:len(file.path)] == file.path or file.path[:len(written)] == written):
            found.append(f"{where}: collides with docs.{'/'.join(doc.path)}, written to {'/'.join(written)}")
    return found


def _file_source(spec: Mapping[Any, Any], where: str, has_file: Callable[[str], bool],
                 folder_files: Callable[[str], tuple[str, ...] | None], problems: list[str]) -> str | None:
    if _text(spec.get("from")) and not has_file(spec["from"]) and folder_files(spec["from"]):
        problems.append(f"{where}.from: '{spec['from']}' is a folder, not a file: end the key with / to copy a folder")
        return None
    return _doc_source(spec, where, False, has_file, problems)


def _folder_source(spec: Mapping[Any, Any], where: str, has_file: Callable[[str], bool],
                   folder_files: Callable[[str], tuple[str, ...] | None], problems: list[str]) -> str | None:
    if "from" not in spec:
        problems.append(f"{where}: missing `from`, the folder")
    elif not _text(spec["from"]):
        problems.append(f"{where}.from: must be a folder name")
    else:
        folder = spec["from"].removesuffix("/")
        held = folder_files(folder)
        if has_file(folder):
            problems.append(f"{where}.from: '{folder}' is a file, not a folder: a folder entry copies a folder")
        elif held is None:
            problems.append(f"{where}.from: no folder '{folder}' next to the architecture file")
        elif not held:
            problems.append(f"{where}.from: the folder '{folder}' holds no file")
        else:
            return folder
    return None


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
        held = spec.get("forbidden", False)
        if not isinstance(held, bool):
            problems.append(f"{where}.forbidden: must be true or false: whether its tests are held to the `forbidden` "
                            "list of the part they mirror")
        for item in subject:
            claimed.setdefault(item.part, name if _line(name) else where)
        if len(problems) == count:
            tiers.append(Tier(name, subject, spec["proves"], spec["may_touch"], spec["litmus"].strip("\n"),
                              spec.get("subject_text", ""), spec.get("one_file_per", ""), spec.get("cases_from", ""),
                              spec.get("data", ""), example, helpers, tuple(p for p in types_only if p in parts),
                              held))
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
        problems.append(f"{where}.path: must be a path such as 'tests/src/billing/api/invoice_checks.py'")
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


def _forbidden(value: Any, parts: dict[str, Part], declared: set[str],
               problems: list[str]) -> dict[str, tuple[tuple[str, ...], ...]]:
    """The names each listed part may not use, in the file's order: a dotted name, or a module by its import name."""
    if not isinstance(value, Mapping):
        problems.append("forbidden: must be a mapping of part names to lists of dotted names, such as "
                        "{<part>: [datetime.datetime.now, socket]}")
        return {}
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name, names in value.items():
        where = f"forbidden.{name}"
        if name not in declared:
            problems.append(f"{where}: no part named {name!r}")
            continue
        if not isinstance(names, list) or not names:
            problems.append(f"{where}: must be a non-empty list of dotted names or import names, such as "
                            "[datetime.datetime.now, socket]")
            continue
        found: list[tuple[str, ...]] = []
        for item in names:
            if not isinstance(item, str) or not _NAME_OR_DOTTED.fullmatch(item):
                problems.append(f"{where}: {item!r} is not a dotted name such as datetime.datetime.now, nor an import "
                                "name such as socket")
            elif tuple(item.split(".")) in found:
                problems.append(f"{where}: {item!r} is listed twice")
            else:
                found.append(tuple(item.split(".")))
        if name in parts:
            forbidden[name] = tuple(found)
    return forbidden


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


def _excluded(value: Any, layout: Layout, problems: list[str]) -> tuple[Excluded, ...]:
    """The folders below the app that are not its source, each with its reason."""
    if not isinstance(value, Mapping):
        problems.append("excluded: must be a mapping of folders below the app to the reason each is not its source, "
                        "such as {vendor: copied code}")
        return ()
    found: list[Excluded] = []
    for key, reason in value.items():
        steps = tuple(key.strip("/").split("/")) if isinstance(key, str) and not key.startswith("/") else ()
        if not steps or any(step in ("", ".", "..") or EACH in step for step in steps):
            problems.append(f"excluded: {key!r} is not a folder below the app, such as vendor/generated")
        elif not _line(reason):
            problems.append(f"excluded.{key}: must give the reason, one line of text")
        elif _resolves(steps, layout):
            problems.append(f"excluded.{key}: '{key}' is a folder of the layout: it is source, not excluded")
        else:
            clash = next((e for e in found if e.path[:len(steps)] == steps[:len(e.path)]), None)
            if clash is not None:
                problems.append(f"excluded.{key}: overlaps the excluded folder '{'/'.join(clash.path)}': list only "
                                "one of the two")
            else:
                found.append(Excluded(steps, reason))
    return tuple(found)


def _hints(value: Any, problems: list[str]) -> dict[str, str]:
    """The project's own advice for a rule id, by rule id."""
    if not isinstance(value, Mapping):
        problems.append("hints: must be a mapping of rule ids to one line of text, such as {rules: see the docs}")
        return {}
    found: dict[str, str] = {}
    for rule, text in value.items():
        if rule not in RULES:
            problems.append(f"hints.{rule}: unknown rule id {rule!r}: use {', '.join(sorted(RULES))}")
        elif not _line(text):
            problems.append(f"hints.{rule}: must be one line of text")
        else:
            found[rule] = text
    return found


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
            framework: Framework | None, problems: list[str]) -> tuple[Guard, ...]:
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
            guard = _scenario_coverage(spec, parts, declared, tiers, framework, where, problems)
            if guard is not None:
                guards.append(guard)
        elif name == "stand-ins":
            if fakes is None or not fakes.prefix:
                problems.append(f"{where}: needs `fakes` with a `prefix`, such as {{path: tests/fakes, for: [<part>], "
                                "prefix: Fake}: the parts whose Protocols the fakes stand in for, where they live and "
                                "how a fake is named")
            else:
                stand_ins = _stand_ins(spec, where, problems)
                if stand_ins is not None:
                    guards.append(stand_ins)
        elif spec not in ({}, None):
            problems.append(f"{where}: takes no parameters: write {{}}")
        elif name == "closed-tree":
            guards.append(ClosedTree())
        else:
            guards.append(NoComments())
    return tuple(guards)


def _scenario_coverage(spec: Any, parts: dict[str, Part], declared: set[str], tiers: tuple[Tier, ...],
                       framework: Framework | None, where: str, problems: list[str]) -> ScenarioCoverage | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{results, tier, suffix, columns, table, file}}: the part holding "
                        "the result unions, the tier whose test files hold their tables, how a union's name ends, the "
                        "three names of a table's parameters (its state, its command and its result), how the table "
                        "is written, and the name of a use case's test file")
        return None
    count = len(problems)
    problems += _unknown_keys(spec, _SCENARIO_KEYS, where)
    problems += [f"{where}: missing `{key}`" for key in sorted(_SCENARIO_KEYS) if key not in spec]
    if len(problems) != count:
        return None
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
    table = _case_table(spec["table"], f"{where}.table", problems)
    file = _use_case_file(spec["file"], framework, f"{where}.file", problems)
    if len(problems) != count or columns is None or table is None or file is None:
        return None
    return ScenarioCoverage(results, tier, suffix, columns, table, file)


def _case_table(value: Any, where: str, problems: list[str]) -> CaseTable | None:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{decorator, row, id}}, and optionally keywords: the dotted names "
                        "of the table's decorator and of its row, the keyword of a row's id, and the keywords the "
                        "decorator's two arguments may be given by")
        return None
    count = len(problems)
    problems += _unknown_keys(value, _TABLE_KEYS, where)
    problems += [f"{where}: missing `{key}`" for key in _TABLE_REQUIRED if key not in value]
    decorator = _dotted(value["decorator"], f"{where}.decorator", problems) if "decorator" in value else None
    row = _dotted(value["row"], f"{where}.row", problems) if "row" in value else None
    if "id" in value and not (isinstance(value["id"], str) and value["id"].isidentifier()):
        problems.append(f"{where}.id: must be a keyword name")
    keywords = value.get("keywords")
    if "keywords" in value and not (isinstance(keywords, list) and len(keywords) == 2 and len(set(keywords)) == 2
                                    and all(isinstance(k, str) and k.isidentifier() for k in keywords)):
        problems.append(f"{where}.keywords: must be two keyword names, the decorator's names and its rows, "
                        "such as [names, rows]")
    if len(problems) != count or decorator is None or row is None:
        return None
    return CaseTable(decorator, row, value["id"], (keywords[0], keywords[1]) if keywords else None)


def _use_case_file(value: Any, framework: Framework | None, where: str, problems: list[str]) -> str | None:
    if not isinstance(value, str) or value.count(NAME) != 1:
        problems.append(f"{where}: must hold `{NAME}` once, such as a_{NAME}.py")
        return None
    name = value.replace(NAME, "x")
    if not _FILE_NAME.fullmatch(name):
        problems.append(f"{where}: must be a file name below the test folders, such as a_{NAME}.py")
        return None
    if framework is not None and not any(fnmatchcase(name, pattern) for pattern in framework.files):
        problems.append(f"{where}: {value!r} is not a name `tests.files` recognises as a test file")
        return None
    return value


def _dotted(value: Any, where: str, problems: list[str]) -> tuple[str, ...] | None:
    """A dotted name such as pkg.sub.name, the path an absolute import binds."""
    if not isinstance(value, str) or not _DOTTED.fullmatch(value):
        problems.append(f"{where}: {value!r} is not a dotted name such as pkg.sub.name")
        return None
    return tuple(value.split("."))


def _dotted_names(value: Any, where: str, problems: list[str]) -> tuple[tuple[str, ...], ...] | None:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of dotted names such as pkg.sub.Name")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        name = _dotted(item, where, problems)
        if name is not None and name in found:
            problems.append(f"{where}: {item!r} is listed twice")
        elif name is not None:
            found.append(name)
    return tuple(found)


def _stand_ins(spec: Any, where: str, problems: list[str]) -> StandIns | None:
    if not isinstance(spec, Mapping):
        problems.append(f"{where}: must be a mapping {{mocks, spec}}, and optionally autospec and fixtures: the dotted "
                        "names of the calls that build a mock, the keywords a mock is given its spec by, and the "
                        "parameters of a test function whose methods build one")
        return None
    count = len(problems)
    problems += _unknown_keys(spec, _STAND_INS_KEYS, where)
    problems += [f"{where}: missing `{key}`" for key in ("mocks", "spec") if key not in spec]
    mocks = _dotted_names(spec["mocks"], f"{where}.mocks", problems) if "mocks" in spec else None
    autospec = _dotted_names(spec["autospec"], f"{where}.autospec", problems) if "autospec" in spec else ()
    for name in (autospec or ()):
        if mocks and name in mocks:
            problems.append(f"{where}.autospec: {'.'.join(name)!r} is also listed in mocks")
    keywords = _identifiers(spec["spec"], f"{where}.spec", problems, "keyword", "[spec]") if "spec" in spec else None
    fixtures = _fixtures(spec["fixtures"], f"{where}.fixtures", problems) if "fixtures" in spec else ()
    if len(problems) != count or mocks is None or autospec is None or keywords is None or fixtures is None:
        return None
    return StandIns(mocks, autospec, keywords, fixtures)


def _fixtures(value: Any, where: str, problems: list[str]) -> tuple[Fixture, ...] | None:
    """The parameters whose methods build mocks, each as {mocks: [...], autospec: [...]}."""
    if not isinstance(value, Mapping) or not value:
        problems.append(f"{where}: must be a mapping of parameter names to {{mocks}}, and optionally autospec: the "
                        "names of the methods that build a mock, and of those that build one from a spec given as an "
                        "argument")
        return None
    count = len(problems)
    found: list[Fixture] = []
    for name, spec in value.items():
        if not isinstance(name, str) or not name.isidentifier():
            problems.append(f"{where}: {name!r} is not a parameter name")
            continue
        at = f"{where}.{name}"
        if not isinstance(spec, Mapping):
            problems.append(f"{at}: must be a mapping {{mocks}}, and optionally autospec")
            continue
        before = len(problems)
        problems += _unknown_keys(spec, _FIXTURE_KEYS, at)
        problems += [f"{at}: missing `mocks`"] if "mocks" not in spec else []
        mocks = _identifiers(spec["mocks"], f"{at}.mocks", problems, "method", "[build]") if "mocks" in spec else None
        autospec = (_identifiers(spec["autospec"], f"{at}.autospec", problems, "method", "[build]")
                    if "autospec" in spec else ())
        problems += [f"{at}.autospec: {method!r} is also listed in mocks" for method in autospec or ()
                     if mocks and method in mocks]
        if len(problems) == before and mocks is not None and autospec is not None:
            found.append(Fixture(name, mocks, autospec))
    return tuple(found) if len(problems) == count else None


def _identifiers(value: Any, where: str, problems: list[str], noun: str, example: str) -> tuple[str, ...] | None:
    """A non-empty list of names, each once, each a plain identifier: the keywords of a call, the methods of an object."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of {noun} names such as {example}")
        return None
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.isidentifier():
            problems.append(f"{where}: {item!r} is not a {noun} name")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def _framework(value: Any, problems: list[str]) -> Framework | None:
    where = "tests"
    if not isinstance(value, Mapping):
        problems.append("tests: must be a mapping {files, functions}: the patterns of a test file's name and of a test "
                        "function's")
        return None
    count = len(problems)
    problems += _unknown_keys(value, _TESTS_KEYS | _TESTS_OPTIONAL, where)
    problems += [f"{where}: missing `{key}`" for key in sorted(_TESTS_KEYS) if key not in value]
    files = _file_patterns(value["files"], problems) if "files" in value else None
    skips = _dotted_names(value["skips"], f"{where}.skips", problems) if "skips" in value else ()
    functions = value.get("functions")
    if "functions" in value and not (isinstance(functions, str) and _FUNCTION_PATTERN.fullmatch(functions)
                                     and functions.replace("*", "x").isidentifier()):
        problems.append(f"{where}.functions: must be a function name pattern: a name with `*` for any text")
    if len(problems) != count or files is None or skips is None:
        return None
    return Framework(files, functions, skips)


def _file_patterns(value: Any, problems: list[str]) -> tuple[str, ...] | None:
    where = "tests.files"
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of file name patterns, each a .py name with `*` for any "
                        "text")
        return None
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not _FILE_PATTERN.fullmatch(item):
            problems.append(f"{where}: {item!r} is not a file name pattern: a name ending in .py, with `*` for any "
                            "text")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def _needs_tests(document: Mapping[Any, Any], tiers: tuple[Tier, ...]) -> list[str]:
    guards = document.get("guards")
    names = [f"`guards.{name}`" for name in ("scenario-coverage", "stand-ins")
             if isinstance(guards, Mapping) and name in guards]
    needing = (["`tiers`"] if tiers or "tiers" in document else []) + names
    if not needing:
        return []
    return [f"missing `tests`: {_and(needing)} must recognise a test file by its name: add "
            "tests: {files: [<pattern>, ...], functions: <pattern>}"]


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


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
