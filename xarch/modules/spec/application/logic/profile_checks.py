"""Checks of a profile file's values that the loader of format 2 shares between its keys: each takes the value found at a key, appends
every problem it finds to `problems` (each naming the key by its address, as the caller gives it) and returns what it
parsed, or None when it found problems. The keys a mapping accepts come from profile_keys for the maps both versions
write the same way."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from fnmatch import fnmatchcase
from typing import Any

from xarch.kernel.logic import names
from xarch.kernel.logic.placement import place_of
from xarch.kernel.placement import EACH
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of
from xarch.modules.spec.application.logic.layout_walk import lies_in
from xarch.modules.spec.application.logic.profile_listing import listing_in
from xarch.modules.spec.application.logic.project_files import APP_PLACEHOLDER
from xarch.modules.spec.domain.profile_keys import FILE, NAMING, PAGE, TABLE
from xarch.modules.spec.domain.values import NAME, Doc, FileEntry, Language, Layout, Naming, Part, Tier
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework

PART_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
"""What a profile calls a part: letters, digits, `_` and `-`, not starting with a digit or `-`."""
CALLED = "()"
"""How a method in a `forbidden` list, called on anything, ends: `.absolute()`."""


def is_name(text: str, language: Language) -> bool:
    """Whether text is a name the language allows, as its data file says (any text but nothing when it does not say)."""
    return names.is_name(text, language.names)


def is_dotted(text: str, language: Language, least: int = 1) -> bool:
    """Whether text is names the language allows joined by dots, at least least of them."""
    steps = text.split(".")
    return len(steps) >= least and all(is_name(step, language) for step in steps)


def method_name(item: str, language: Language) -> str | None:
    """The name of the method an item of a `forbidden` list names, `.<name>()`; None when it names none."""
    name = item[1:-len(CALLED)] if item.startswith(".") and item.endswith(CALLED) else ""
    return name if is_name(name, language) else None


def file_pattern(language: Language) -> re.Pattern[str]:
    """What a file name pattern is: letters, digits, `_`, `.`, `-` and `*`, ending in the language's extension."""
    return re.compile(rf"[A-Za-z0-9_.*-]+{re.escape(language.checked.extension)}")


def file_name(language: Language) -> re.Pattern[str]:
    """What a file name is: letters, digits, `_`, `.` and `-`, ending in the language's extension."""
    return re.compile(rf"[A-Za-z0-9_.-]+{re.escape(language.checked.extension)}")


def layer_chains(value: Any, parts: dict[str, Part], declared: set[str], rules: dict[str, tuple[Target, ...]],
            problems: list[str]) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        problems.append("layers: must be a mapping of names to lists of parts, from the inside out")
        return {}
    layers: dict[str, tuple[str, ...]] = {}
    seen: dict[str, str] = {}
    for name, chain in value.items():
        where = f"layers.{name}"
        if not text(name) or not PART_NAME.fullmatch(name):
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


def naming_rows(value: Any, problems: list[str], at: str) -> tuple[Naming, ...]:
    if not isinstance(value, list):
        problems.append(f"{at}: must be a list of rows such as {{kind, where, pattern, example}}")
        return ()
    rows: list[Naming] = []
    for i, spec in enumerate(value):
        where = f"{at}[{i}]"
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping with `kind`, `where`, `pattern` and `example`")
            continue
        count = len(problems)
        problems += unknown_keys(spec, names_of(NAMING), where)
        problems += [f"{where}: missing `{key}`" for key in required_of(NAMING) if key not in spec]
        problems += [f"{where}.{key}: must be a string" for key in ("kind", "pattern")
                     if key in spec and not text(spec[key])]
        lists = {key: strings(spec.get(key)) for key in ("where", "example")}
        problems += [f"{where}.{key}: must be a string or a list of strings" for key, found in lists.items()
                     if key in spec and found is None]
        if len(problems) == count:
            rows.append(Naming(spec["kind"], lists["where"] or (), spec["pattern"], lists["example"] or ()))
    return tuple(rows)


def strings(value: Any) -> tuple[str, ...] | None:
    if text(value):
        return (value,)
    if isinstance(value, list) and value and all(text(v) for v in value):
        return tuple(value)
    return None


def doc_pages(value: Any, listed: Collection[str], problems: list[str], at: str) -> tuple[Doc, ...]:
    """The project docs: files with the template each is filled from, and folders with a note."""
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a mapping of paths to {{from, note}}, such as {{statement.md: {{from: docs/statement.md}}}}")
        return ()
    docs: list[Doc] = []
    files: set[tuple[str, ...]] = set()
    folders: set[tuple[str, ...]] = set()
    for key, spec in value.items():
        where = f"{at}.{key}"
        folder = isinstance(key, str) and key.endswith("/")
        steps = tuple(key.removesuffix("/").split("/")) if isinstance(key, str) else ()
        if not steps or any(step in ("", ".", "..") or "\\" in step for step in steps):
            problems.append(f"{where}: must be a path of plain names below the docs folder")
            continue
        if not isinstance(spec, Mapping):
            problems.append(f"{where}: must be a mapping such as {{from: <file>, note: <text>}}")
            continue
        count = len(problems)
        problems += unknown_keys(spec, names_of(PAGE), where)
        if "note" in spec and not line(spec["note"]):
            problems.append(f"{where}.note: must be one line of text")
        source = doc_source(spec, where, folder, listed, problems)
        if len(problems) == count:
            docs.append(Doc(steps, source, spec.get("note", "")))
            (folders if folder else files).add(steps)
    for doc in docs:
        problems += doc_clashes(doc, files, folders, at)
    return tuple(docs)


def init_files(value: Any, docs: tuple[Doc, ...], files: Collection[str], problems: list[str],
               docs_at: str, language: Language) -> tuple[FileEntry, ...]:
    """The project files: each path below the project root with the template, or the folder, it is written from."""
    if not isinstance(value, Mapping):
        problems.append("files: must be a mapping of paths to {from}, such as {tests/rules"
                        f"{language.checked.extension}: {{from: guard{language.checked.extension}}}}}")
        return ()
    found: list[FileEntry] = []
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
        problems += unknown_keys(spec, names_of(FILE), where)
        source = (folder_source(spec, where, files, problems) if folder
                  else file_source(spec, where, files, problems))
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
            found.append(FileEntry(steps, source or "", pinned, folder, fill))
    for file in found:
        problems += file_clashes(file, found, docs, docs_at)
    return tuple(found)


def entry(file: FileEntry) -> str:
    return "/".join(file.path) + ("/" if file.folder else "")


def file_clashes(file: FileEntry, files: list[FileEntry], docs: tuple[Doc, ...],
                 docs_at: str) -> list[str]:
    where = f"files.{entry(file)}"
    found = [f"{where}: '{'/'.join(file.path[:i])}' is a file, not a folder"
             for i in range(1, len(file.path)) if any(o.path == file.path[:i] and not o.folder for o in files)]
    for other in files:
        if not other.folder or other is file:
            continue
        if file.path == other.path:
            found.append(f"{where}: is also a folder entry")
        elif file.path[:len(other.path)] == other.path:
            found.append(f"{where}: lies inside the folder entry '{entry(other)}'")
    for doc in docs:
        written = DOCS_ROOT + doc.path
        if doc.source is not None and (written[:len(file.path)] == file.path or file.path[:len(written)] == written):
            found.append(f"{where}: collides with {docs_at}.{'/'.join(doc.path)}, written to {'/'.join(written)}")
    return found


def file_source(spec: Mapping[Any, Any], where: str, files: Collection[str], problems: list[str]) -> str | None:
    if text(spec.get("from")) and spec["from"] not in files and listing_in(files, spec["from"]):
        problems.append(f"{where}.from: '{spec['from']}' is a folder, not a file: end the key with / to copy a folder")
        return None
    return doc_source(spec, where, False, files, problems)


def folder_source(spec: Mapping[Any, Any], where: str, files: Collection[str], problems: list[str]) -> str | None:
    if "from" not in spec:
        problems.append(f"{where}: missing `from`, the folder")
    elif not text(spec["from"]):
        problems.append(f"{where}.from: must be a folder name")
    else:
        folder = spec["from"].removesuffix("/")
        held = listing_in(files, folder)
        if folder in files:
            problems.append(f"{where}.from: '{folder}' is a file, not a folder: a folder entry copies a folder")
        elif held is None:
            problems.append(f"{where}.from: no folder '{folder}' next to the architecture file")
        else:
            return folder
    return None


def doc_source(spec: Mapping[Any, Any], where: str, folder: bool, files: Collection[str],
               problems: list[str]) -> str | None:
    if folder:
        if "from" in spec:
            problems.append(f"{where}: a folder takes only `note`")
        return None
    if "from" not in spec:
        problems.append(f"{where}: missing `from`, the template file")
    elif not text(spec["from"]):
        problems.append(f"{where}.from: must be a file name")
    elif spec["from"] not in files:
        problems.append(f"{where}.from: no file '{spec['from']}' next to the architecture file")
    else:
        return spec["from"]
    return None


def doc_clashes(doc: Doc, files: set[tuple[str, ...]], folders: set[tuple[str, ...]], at: str) -> list[str]:
    where = f"{at}.{'/'.join(doc.path)}{'/' if doc.is_folder else ''}"
    found = [f"{where}: '{'/'.join(doc.path[:i])}' is a file, not a folder"
             for i in range(1, len(doc.path)) if doc.path[:i] in files]
    if doc.is_folder and not any(f[:len(doc.path)] == doc.path and len(f) > len(doc.path) for f in files):
        found.append(f"{where}: holds no file")
    return found


def tier_folder(value: Any, parts: dict[str, Part], where: str, problems: list[str],
                language: Language) -> tuple[str, ...] | None:
    """The folder below the tests folder where a tier's tests live when they mirror no part."""
    steps = tuple(value.split("/")) if line(value) and not value.startswith("/") else ()
    if not steps or any(step in ("", ".", "..") or EACH in step for step in steps):
        problems.append(f"{where}: must be a folder below the tests folder, such as architecture: relative, with no "
                        "`..`, no empty step and no `*`")
        return None
    mirrored = place_of({name: part.path for name, part in parts.items()}, steps, language.checked.marks).part
    if mirrored is not None:
        problems.append(f"{where}: '{value}' is the folder of part '{mirrored}', which places its tests: give `folder` "
                        "only to a folder that mirrors no part")
        return None
    return steps


def folder_clashes(tiers: tuple[Tier, ...], fakes: Fakes | None) -> list[str]:
    """The folders of tiers that lie inside, or hold, the fakes' folder or another tier's."""
    problems: list[str] = []
    taken = [(f"the fakes' folder '{'/'.join(fakes.folder)}'", fakes.folder)] if fakes is not None else []
    for tier in tiers:
        if tier.folder is None:
            continue
        shown = "/".join(tier.folder)
        problems += [f"tiers: the folder '{shown}' of tier '{tier.name}' overlaps {owner}: give each its own folder"
                     for owner, other in taken if overlap(tier.folder, other)]
        taken.append((f"the folder '{shown}' of tier '{tier.name}'", tier.folder))
    return problems


def overlap(first: tuple[str, ...], second: tuple[str, ...]) -> bool:
    return first[:len(second)] == second or second[:len(first)] == first


def excluded_folders(value: Any, layout: Layout, problems: list[str]) -> tuple[Excluded, ...]:
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
        elif not line(reason):
            problems.append(f"excluded.{key}: must give the reason, one line of text")
        elif lies_in(layout, steps):
            problems.append(f"excluded.{key}: '{key}' is a folder of the layout: it is source, not excluded")
        else:
            clash = next((e for e in found if e.path[:len(steps)] == steps[:len(e.path)]), None)
            if clash is not None:
                problems.append(f"excluded.{key}: overlaps the excluded folder '{'/'.join(clash.path)}': list only "
                                "one of the two")
            else:
                found.append(Excluded(steps, reason))
    return tuple(found)


def rule_hints(value: Any, problems: list[str], own: Collection[str] = ()) -> dict[str, str]:
    """The project's own advice for a rule id, by rule id: a check xarch has, or one of the profile's own (own)."""
    if not isinstance(value, Mapping):
        problems.append("hints: must be a mapping of rule ids to one line of text, such as {rules: see the docs}")
        return {}
    found: dict[str, str] = {}
    for rule, text in value.items():
        if rule not in RULES and rule not in own:
            problems.append(f"hints.{rule}: unknown rule id {rule!r}: use {', '.join(sorted((*RULES, *own)))}")
        elif not line(text):
            problems.append(f"hints.{rule}: must be one line of text")
        else:
            found[rule] = text
    return found


def part_names(value: Any, declared: set[str], where: str, problems: list[str]) -> list[str]:
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


def case_table(value: Any, where: str, problems: list[str], language: Language) -> CaseTable | None:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{decorator, row, id}}, and optionally keywords: the dotted names "
                        "of the table's decorator and of its row, the keyword of a row's id, and the keywords the "
                        "decorator's two arguments may be given by")
        return None
    count = len(problems)
    problems += unknown_keys(value, names_of(TABLE), where)
    problems += [f"{where}: missing `{key}`" for key in required_of(TABLE) if key not in value]
    decorator = dotted(value["decorator"], f"{where}.decorator", problems, language) if "decorator" in value else None
    row = dotted(value["row"], f"{where}.row", problems, language) if "row" in value else None
    if "id" in value and not (isinstance(value["id"], str) and is_name(value["id"], language)):
        problems.append(f"{where}.id: must be a keyword name")
    keywords = value.get("keywords")
    if "keywords" in value and not (isinstance(keywords, list) and len(keywords) == 2 and len(set(keywords)) == 2
                                    and all(isinstance(k, str) and is_name(k, language) for k in keywords)):
        problems.append(f"{where}.keywords: must be two keyword names, the decorator's names and its rows, "
                        "such as [names, rows]")
    if len(problems) != count or decorator is None or row is None:
        return None
    return CaseTable(decorator, row, value["id"], (keywords[0], keywords[1]) if keywords else None)


def use_case_file(value: Any, framework: Framework | None, where: str, problems: list[str], language: Language,
                  files_key: str = "tests.files") -> str | None:
    if not isinstance(value, str) or value.count(NAME) != 1:
        problems.append(f"{where}: must hold `{NAME}` once, such as a_{NAME}{language.checked.extension}")
        return None
    name = value.replace(NAME, "x")
    if not file_name(language).fullmatch(name):
        problems.append(f"{where}: must be a file name below the test folders, such as a_{NAME}{language.checked.extension}")
        return None
    if framework is not None and not any(fnmatchcase(name, pattern) for pattern in framework.files):
        problems.append(f"{where}: {value!r} is not a name `{files_key}` recognises as a test file")
        return None
    return value


def dotted(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, ...] | None:
    """A dotted name such as pkg.sub.name, the path an absolute import binds."""
    if not isinstance(value, str) or not is_dotted(value, language, 2):
        problems.append(f"{where}: {value!r} is not a dotted name such as pkg.sub.name")
        return None
    return tuple(value.split("."))


def dotted_names(value: Any, where: str, problems: list[str], language: Language) -> tuple[tuple[str, ...], ...] | None:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of dotted names such as pkg.sub.Name")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        name = dotted(item, where, problems, language)
        if name is not None and name in found:
            problems.append(f"{where}: {item!r} is listed twice")
        elif name is not None:
            found.append(name)
    return tuple(found)


def fixtures(value: Any, where: str, problems: list[str], language: Language,
             calls: str = "mocks") -> tuple[Fixture, ...] | None:
    """The parameters whose methods build mocks, each as {<calls>: [...], autospec: [...]}; `calls` is the key naming
    the methods that build a mock."""
    if not isinstance(value, Mapping) or not value:
        problems.append(f"{where}: must be a mapping of parameter names to {{{calls}}}, and optionally autospec: the "
                        "names of the methods that build a mock, and of those that build one from a spec given as an "
                        "argument")
        return None
    count = len(problems)
    found: list[Fixture] = []
    for name, spec in value.items():
        if not isinstance(name, str) or not is_name(name, language):
            problems.append(f"{where}: {name!r} is not a parameter name")
            continue
        at = f"{where}.{name}"
        if not isinstance(spec, Mapping):
            problems.append(f"{at}: must be a mapping {{{calls}}}, and optionally autospec")
            continue
        before = len(problems)
        problems += unknown_keys(spec, {calls, "autospec"}, at)
        problems += [f"{at}: missing `{calls}`"] if calls not in spec else []
        mocks = identifiers(spec[calls], f"{at}.{calls}", problems, "method", "[build]", language) if calls in spec else None
        autospec = (identifiers(spec["autospec"], f"{at}.autospec", problems, "method", "[build]", language)
                    if "autospec" in spec else ())
        problems += [f"{at}.autospec: {method!r} is also listed in {calls}" for method in autospec or ()
                     if mocks and method in mocks]
        if len(problems) == before and mocks is not None and autospec is not None:
            found.append(Fixture(name, mocks, autospec))
    return tuple(found) if len(problems) == count else None


def identifiers(value: Any, where: str, problems: list[str], noun: str, example: str,
                language: Language) -> tuple[str, ...] | None:
    """A non-empty list of names, each once, each a plain identifier: the keywords of a call, the methods of an object."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of {noun} names such as {example}")
        return None
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not is_name(item, language):
            problems.append(f"{where}: {item!r} is not a {noun} name")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def framework_patterns(value: Any, problems: list[str], where: str, known: Collection[str],
                       language: Language) -> Framework | None:
    """How the test framework names test files and functions, the map written at `where`; `known` are the keys the
    map may hold, which the caller may widen with what it reads itself."""
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{files, functions}}: the patterns of a test file's name and of a "
                        "test function's")
        return None
    count = len(problems)
    problems += unknown_keys(value, known, where)
    problems += [f"{where}: missing `{key}`" for key in ("files", "functions") if key not in value]
    files = file_patterns(value["files"], problems, f"{where}.files", language) if "files" in value else None
    skips = dotted_names(value["skips"], f"{where}.skips", problems, language) if "skips" in value else ()
    functions = value.get("functions")
    if "functions" in value and not (isinstance(functions, str)
                                     and is_name(functions.replace("*", "x"), language)):
        problems.append(f"{where}.functions: must be a function name pattern: a name with `*` for any text")
    if len(problems) != count or files is None or skips is None:
        return None
    return Framework(files, functions, skips)


def file_patterns(value: Any, problems: list[str], where: str, language: Language) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of file name patterns, each a {language.checked.extension} name "
                        "with `*` for any text")
        return None
    pattern = file_pattern(language)
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not pattern.fullmatch(item):
            problems.append(f"{where}: {item!r} is not a file name pattern: a name ending in {language.checked.extension}, "
                            "with `*` for any text")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def join_and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def column_names(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, str, str] | None:
    if not isinstance(value, list) or len(value) != 3 or not all(isinstance(v, str) for v in value):
        problems.append(f"{where}: must be a list of three names, such as [given, when, then]")
        return None
    count = len(problems)
    for i, name in enumerate(value):
        if not is_name(name, language):
            problems.append(f"{where}: {name!r} is not a name a parameter can have")
        elif name in value[:i]:
            problems.append(f"{where}: {name!r} is listed twice")
    return (value[0], value[1], value[2]) if len(problems) == count else None


def unknown_keys(spec: Mapping[Any, Any], known: Collection[str], where: str) -> list[str]:
    unknown = sorted(str(k) for k in spec if k not in known)
    if not unknown:
        return []
    return [f"{where}: unknown key{'s' if len(unknown) > 1 else ''} {quoted(unknown)}: use {', '.join(sorted(known))}"]


def text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def line(value: Any) -> bool:
    return text(value) and "\n" not in value


def string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def quoted(names: list[str]) -> str:
    return ", ".join(f"'{n}'" for n in names)


def reserved_modules(value: Any, problems: list[str], language: Language) -> dict[str, str]:
    """The standard-library modules the profile reserves, by top-level import name, each with why."""
    if not isinstance(value, Mapping):
        problems.append("reserved: must be a mapping of standard-library names to why they are reserved, such as "
                        "{ast: only the reader parses the language}")
        return {}
    found: dict[str, str] = {}
    for name, reason in value.items():
        if not isinstance(name, str) or not is_name(name, language):
            problems.append(f"reserved: {name!r} is not a top-level import name, such as ast")
        elif name not in language.standard_names:
            problems.append(f"reserved: {name!r} is not in the {language.checked.title} standard library: an outside package "
                            "is imported only by the parts whose `libraries` list it already")
        elif not line(reason):
            problems.append(f"reserved.{name}: must say in one line why it is reserved")
        else:
            found[name] = reason
    return found


def package_names(value: Any, where: str, problems: list[str], language: Language,
                  reserved: Collection[str] = ()) -> tuple[str, ...] | None:
    """The outside packages a part may import, by top-level import name; the standard library is no entry, but for a
    module the profile reserves."""
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of top-level import names, such as [sqlmodel]")
        return None
    found: list[str] = []
    for package in value:
        if not isinstance(package, str) or not is_name(package, language):
            problems.append(f"{where}: {package!r} is not a top-level import name, such as sqlmodel")
        elif package in language.standard_names and package not in reserved:
            problems.append(f"{where}: {package!r} is in the standard library, which every part may import unless "
                            "`reserved` names it")
        elif package in found:
            problems.append(f"{where}: {package!r} is listed twice")
        else:
            found.append(package)
    return tuple(found)


def forbidden_names(value: Any, where: str, problems: list[str],
                    language: Language) -> tuple[tuple[str, ...], ...] | None:
    """The names a part may not use: dotted names, or modules by their import name; a builtin is written in the
    language's namespace for them, <namespace>.<name>. A method called on anything is written `.<name>()` and kept as
    written, split at its dot: ("", "<name>()")."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of dotted names or import names, such as "
                        "[datetime.datetime.now, socket]")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        method = method_name(item, language) if isinstance(item, str) else None
        if method is not None and language.checked.is_special(method):
            problems.append(f"{where}: {item!r} is a special method, which no code calls by name")
        elif method is None and isinstance(item, str) and item.startswith(".") and is_name(item[1:], language):
            problems.append(f"{where}: {item!r} is neither a dotted name nor a method: write {item}() for a method "
                            "called on anything")
        elif method is None and (not isinstance(item, str) or not is_dotted(item, language)):
            problems.append(f"{where}: {item!r} is not a dotted name such as datetime.datetime.now, nor an import "
                            "name such as socket, nor a method such as .absolute()")
        elif "." not in item and item in language.builtin_names:
            problems.append(f"{where}: {item!r} is a {language.checked.title} builtin, which a bare name does not ban: write "
                            f"{language.namespace}.{item}")
        elif tuple(item.split(".")) in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(tuple(item.split(".")))
    return tuple(found)


def scenario_places(results: Any, tier: Any, suffix: Any, parts: dict[str, Part], declared: set[str],
                    tiers: tuple[Tier, ...], where: str, problems: list[str], language: Language) -> None:
    """The part holding the result unions lies in a repeating folder, the tier is declared and tests that part, and the
    suffix is the end of a name."""
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
    if not isinstance(suffix, str) or not is_name(suffix, language):
        problems.append(f"{where}.suffix: must be the end of a name, such as Result")
