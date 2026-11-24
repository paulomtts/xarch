"""Checks of a profile file's values that the loader shares between its keys: each takes the value found at a key, appends
every problem it finds to `problems` (each naming the key by its address, as the caller gives it) and returns what it
parsed, or None when it found problems. The keys a mapping accepts come from key_table for the maps both versions
write the same way."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from fnmatch import fnmatchcase
from typing import Any

from xarch.kernel.logic import names
from xarch.kernel.logic.cases import CASED, CASES, filled
from xarch.kernel.logic.placement import place_of
from xarch.kernel.logic.targets import outside_imports
from xarch.kernel.placement import EACH
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.docs_files import DOCS_ROOT
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of, retired
from xarch.modules.spec.application.logic.layout_walk import lies_in
from xarch.modules.spec.application.logic.outside_name import outside_name
from xarch.modules.spec.application.logic.profile_listing import listing_in
from xarch.modules.spec.application.logic.project_files import APP_PLACEHOLDER
from xarch.modules.spec.domain.profile_keys import DECLARED, FILE, FIXTURE, NAMING, PAGE, RULE_ID, TABLES
from xarch.modules.spec.domain.values import NAME, Doc, FileEntry, Language, Layout, Naming, Part, Tier
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import SPEC_FORMS
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import (
    Fakes,
    Fixture,
    Framework,
    Place,
    RowId,
    SpecEntry,
    TableForm,
    TestForm,
)

PART_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
"""What a profile calls a part: letters, digits, `_` and `-`, not starting with a digit or `-`."""
CALLED = "()"
"""How a method in a `never` list, called on anything, ends: `.absolute()`."""
HOLDERS = ("decorator", "call", "loop")
"""The keys of a table form that say what holds its rows, exactly one of them in each."""
DECLARING = ("function", "call")
"""The keys of a form that declares a test that say how it declares one, exactly one of them in each."""
CALL_SLOTS = ("title", "body")
"""The slots of a call form: where the test's title and its body are among the call's arguments."""
PARAMETERS = "parameters"
"""What columns_from says of a form whose column names are the test's own parameters."""
BOUND = "bound"
"""What columns_from says of a loop whose column names are the names it binds."""
FIELDS = "fields"
"""What columns_from says of a form whose column names are the fields of each row."""
LITERAL = "literal"
"""What `row` says of a form whose rows are literals, not calls."""
PLACE = "must be {position: <n>, keyword: <name>}, at least one of them, of the holder's arguments"
"""What the loader says of a place of a table form that is none."""


def _outside(text: str, language: Language, namespace: str = "") -> tuple[str, ...] | None:
    """The steps of an outside name as the language writes one (see outside_name); None when the text is none."""
    return outside_name(text, language.names, language.checked.package, language.checked.member, namespace)


def _such(language: Language) -> str:
    """How a message shows an outside name of the language: <package>, its member, <name>."""
    return f"<package>{language.checked.member}<name>"


def _is_package(text: Any, language: Language) -> bool:
    """Whether text names a package alone, as the language's package pattern says one is; never its namespace."""
    steps = _outside(text, language) if isinstance(text, str) else None
    return steps is not None and len(steps) == 1


def _method_name(item: str, language: Language) -> str | None:
    """The name of the method an item of a `never` list names, `.<name>()`; None when it names none."""
    name = item[1:-len(CALLED)] if item.startswith(".") and item.endswith(CALLED) else ""
    return name if names.is_name(name, language.names) else None


def endings(language: Language) -> str:
    """The endings of a source file of the language, as a refusal lists them: one alone, or all but the last joined by
    commas and the last after `or`."""
    *rest, last = language.checked.extensions or ("",)
    return f"{', '.join(rest)} or {last}" if rest else last


def _ending(language: Language) -> str:
    """A regular expression any one of the language's endings matches."""
    return "|".join(re.escape(extension) for extension in language.checked.extensions)


def _file_pattern(language: Language) -> re.Pattern[str]:
    """What a file name pattern is: no `/`, at least one character, then one of the language's endings; `*` stands
    for any text."""
    return re.compile(rf"[^/]+(?:{_ending(language)})")


def _file_name(language: Language) -> re.Pattern[str]:
    """What a file name is: no `/` and no `*`, at least one character, then one of the language's endings."""
    return re.compile(rf"[^/*]+(?:{_ending(language)})")


def layer_chains(value: Any, parts: dict[str, Part], declared: set[str], rules: dict[str, tuple[Target, ...]],
                 problems: list[str], *, words: Collection[str]) -> dict[str, tuple[str, ...]]:
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
            if (prefixed := outside_imports(part, declared, words)) is not None:
                problems.append(f"{where}: {prefixed}")
                ok = False
            elif not isinstance(part, str) or part not in declared:
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
        problems += unknown_keys(spec, names_of(NAMING), where, NAMING)
        problems += [f"{where}: missing `{key}`" for key in required_of(NAMING) if key not in spec]
        problems += [f"{where}.{key}: must be a string" for key in ("kind", "pattern")
                     if key in spec and not text(spec[key])]
        lists = {key: _strings(spec.get(key)) for key in ("where", "example")}
        problems += [f"{where}.{key}: must be a string or a list of strings" for key, found in lists.items()
                     if key in spec and found is None]
        if len(problems) == count:
            rows.append(Naming(spec["kind"], lists["where"] or (), spec["pattern"], lists["example"] or ()))
    return tuple(rows)


def _strings(value: Any) -> tuple[str, ...] | None:
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
        problems += unknown_keys(spec, names_of(PAGE), where, PAGE)
        if "note" in spec and not line(spec["note"]):
            problems.append(f"{where}.note: must be one line of text")
        source = _doc_source(spec, where, folder, listed, problems)
        if len(problems) == count:
            docs.append(Doc(steps, source, spec.get("note", "")))
            (folders if folder else files).add(steps)
    for doc in docs:
        problems += _doc_clashes(doc, files, folders, at)
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
        problems += unknown_keys(spec, names_of(FILE), where, FILE)
        source = (_folder_source(spec, where, files, problems) if folder
                  else _file_source(spec, where, files, problems))
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
        problems += _file_clashes(file, found, docs, docs_at)
    return tuple(found)


def _entry(file: FileEntry) -> str:
    return "/".join(file.path) + ("/" if file.folder else "")


def _file_clashes(file: FileEntry, files: list[FileEntry], docs: tuple[Doc, ...],
                 docs_at: str) -> list[str]:
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
            found.append(f"{where}: collides with {docs_at}.{'/'.join(doc.path)}, written to {'/'.join(written)}")
    return found


def _file_source(spec: Mapping[Any, Any], where: str, files: Collection[str], problems: list[str]) -> str | None:
    if text(spec.get("from")) and spec["from"] not in files and listing_in(files, spec["from"]):
        problems.append(f"{where}.from: '{spec['from']}' is a folder, not a file: end the key with / to copy a folder")
        return None
    return _doc_source(spec, where, False, files, problems)


def _folder_source(spec: Mapping[Any, Any], where: str, files: Collection[str], problems: list[str]) -> str | None:
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


def _doc_source(spec: Mapping[Any, Any], where: str, folder: bool, files: Collection[str],
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


def _doc_clashes(doc: Doc, files: set[tuple[str, ...]], folders: set[tuple[str, ...]], at: str) -> list[str]:
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
                     for owner, other in taken if _overlap(tier.folder, other)]
        taken.append((f"the folder '{shown}' of tier '{tier.name}'", tier.folder))
    return problems


def _overlap(first: tuple[str, ...], second: tuple[str, ...]) -> bool:
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
        problems.append("hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}")
        return {}
    found: dict[str, str] = {}
    for rule, text in value.items():
        if rule not in RULES and rule not in own:
            problems.append(f"hints.{rule}: unknown rule id {rule!r}: {advice(RULE_ID, str(rule), (*RULES, *own))}")
        elif not line(text):
            problems.append(f"hints.{rule}: must be one line of text")
        else:
            found[rule] = text
    return found


def part_names(value: Any, declared: Collection[str], where: str, problems: list[str], *,
               words: Collection[str]) -> list[str]:
    """The parts a key outside `imports` names, by their plain names, in the order written; a name that is no part
    declared, one written as a reference (its prefix `parts` or one of words), or one listed twice adds its problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of part names")
        return []
    found: list[str] = []
    for name in value:
        if (prefixed := outside_imports(name, declared, words)) is not None:
            problems.append(f"{where}: {prefixed}")
        elif not isinstance(name, str) or name not in declared:
            problems.append(f"{where}: no part named {name!r}")
        elif name in found:
            problems.append(f"{where}: {name!r} is listed twice")
        else:
            found.append(name)
    return found


def use_case_file(value: Any, framework: Framework | None, where: str, problems: list[str], language: Language,
                  files_key: str = "testing.files") -> str | None:
    such = f"such as a_{CASED[0]}{language.checked.extension}"
    if isinstance(value, str) and NAME in value:
        problems.append(f"{where}: {value!r}: {NAME} with no case was removed in 0.3.0: write {CASED[0]} for what "
                        f"{NAME} meant")
        return None
    if not isinstance(value, str) or sum(value.count(cased) for cased in CASED) != 1:
        problems.append(f"{where}: must hold `{{name:<case>}}` once, <case> one of {', '.join(CASES)}, {such}")
        return None
    name = filled(value, "x")
    if not _file_name(language).fullmatch(name):
        problems.append(f"{where}: must be a file name below the test folders, {such}")
        return None
    if framework is not None and not any(fnmatchcase(name, pattern) for pattern in framework.files):
        problems.append(f"{where}: {value!r} is not a name `{files_key}` recognises as a test file")
        return None
    return value


def table_forms(value: Any, where: str, problems: list[str], language: Language) -> tuple[TableForm, ...] | None:
    """The forms a table of cases is written in, each entry addressed `<where>.<i>`, i from 0; None when any entry
    has a problem."""
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of table forms, each {{decorator | call | loop, columns_from, rows, "
                        "row, id}")
        return None
    forms = [_table_form(entry, f"{where}.{index}", problems, language) for index, entry in enumerate(value)]
    found = tuple(form for form in forms if form is not None)
    return found if len(found) == len(forms) else None


def _table_form(entry: Any, where: str, problems: list[str], language: Language) -> TableForm | None:
    """One form: exactly one holder, its slots each in the shape the holder takes, and the language able to say its
    row."""
    if not isinstance(entry, Mapping):
        problems.append(f"{where}: must be a mapping with one of decorator, call or loop")
        return None
    count = len(problems)
    problems += unknown_keys(entry, names_of(TABLES), where, TABLES)
    holders = [key for key in HOLDERS if key in entry]
    if len(holders) != 1:
        problems.append(f"{where}: must have exactly one of decorator, call or loop")
    loop = holders == ["loop"]
    needed = (*required_of(TABLES), *(("rows",) if holders in (["decorator"], ["call"]) else ()))
    problems += [f"{where}: missing `{key}`" for key in needed if key not in entry]
    decorator = (_outside_name_at(entry["decorator"], f"{where}.decorator", problems, language)
                 if "decorator" in entry else ())
    calls = outside_names(entry["call"], f"{where}.call", problems, language) if "call" in entry else ()
    if "loop" in entry and entry["loop"] is not True:
        problems.append(f"{where}.loop: must be true: the rows are a list a loop of the test's body runs")
    if "rows" in entry and loop:
        problems.append(f"{where}.rows: a loop runs the rows it iterates: drop rows")
    rows = _place(entry["rows"], f"{where}.rows", problems, language) if "rows" in entry and not loop else None
    row = _row_of(entry["row"], f"{where}.row", problems, language) if "row" in entry else None
    columns = (_columns_from(entry["columns_from"], f"{where}.columns_from", loop, row, problems, language)
               if "columns_from" in entry else None)
    given = _row_id(entry["id"], f"{where}.id", row, problems, language) if "id" in entry else None
    if len(problems) != count or decorator is None or calls is None or row is None or columns is None or given is None:
        return None
    problems += _unwritten(row, given, where, language)
    if len(problems) != count:
        return None
    return TableForm(columns, rows, row, given, decorator, calls, loop)


def _counted(value: Any) -> bool:
    """Whether a value is a whole number from 0 (true and false are no numbers here)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _place(value: Any, where: str, problems: list[str], language: Language) -> Place | None:
    """A place among the holder's arguments: {position, keyword}, at least one of them given, and each one given a
    value of its own (null is none)."""
    position = value.get("position") if isinstance(value, Mapping) else None
    keyword = value.get("keyword") if isinstance(value, Mapping) else None
    if not (isinstance(value, Mapping) and set(value) <= {"position", "keyword"} and value
            and ("position" not in value or _counted(position))
            and ("keyword" not in value or (isinstance(keyword, str) and names.is_name(keyword, language.names)))):
        problems.append(f"{where}: {PLACE}")
        return None
    return Place(position, keyword or "")


def _row_of(value: Any, where: str, problems: list[str], language: Language) -> tuple[str, ...] | None:
    """How a row is written: the steps of the outside name a row calls, or none for a literal row."""
    return () if value == LITERAL else _outside_name_at(value, where, problems, language)


def _columns_from(value: Any, where: str, loop: bool, row: tuple[str, ...] | None, problems: list[str],
                  language: Language) -> Place | str | None:
    """Where the column names come from: a place of the holder's arguments, or one of PARAMETERS, BOUND and FIELDS,
    each where its holder and its row allow it (row None: refused already, and not looked at)."""
    if isinstance(value, Mapping) and loop:
        problems.append(f"{where}: a loop has no arguments: write bound or fields")
        return None
    if isinstance(value, Mapping):
        return _place(value, where, problems, language)
    if value not in (PARAMETERS, BOUND, FIELDS):
        problems.append(f"{where}: must be {{position, keyword}}, parameters, bound or fields")
        return None
    if value == BOUND and not loop:
        problems.append(f"{where}: bound is the names a loop binds: write it with loop")
        return None
    if value == PARAMETERS and loop:
        problems.append(f"{where}: a loop's columns are bound or fields")
        return None
    if value == FIELDS and row:
        problems.append(f"{where}: fields needs row: literal")
        return None
    return str(value)


def _row_id(value: Any, where: str, row: tuple[str, ...] | None, problems: list[str],
            language: Language) -> RowId | None:
    """What gives a row its id: exactly one of {keyword}, {field} and {position}, a keyword only of a row call and a
    field only of a literal row (row None: refused already, and not looked at)."""
    kind, item = next(iter(value.items())) if isinstance(value, Mapping) and len(value) == 1 else ("", None)
    named = isinstance(item, str) and names.is_name(item, language.names)
    if not ((kind in ("keyword", "field") and named) or (kind == "position" and _counted(item))):
        problems.append(f"{where}: must be one of {{keyword: <name>}}, {{field: <name>}} or {{position: <n>}}")
        return None
    if kind == "keyword" and row == ():
        problems.append(f"{where}: {{keyword}} names a keyword of a row call: write a dotted row")
        return None
    if kind == "field" and row:
        problems.append(f"{where}: {{field}} names a field of a literal row: write row: literal")
        return None
    return RowId(**{kind: item})


def _unwritten(row: tuple[str, ...], given: RowId, where: str, language: Language) -> list[str]:
    """The problems of a form the language cannot say: a row call with no `writing.call`, and an id by a keyword or a
    field with no template of its own; an id by position needs none."""
    writing, title = language.checked.writing, language.checked.title
    found: list[str] = []
    if row and not writing.call:
        found.append(f"{where}.row: the language {title} does not write `writing.call`, how a row call is named")
    if given.keyword and not writing.keyword:
        found.append(f"{where}.id: the language {title} does not write `writing.keyword`, how a row's id is given by "
                     "a keyword")
    if given.field and not writing.field:
        found.append(f"{where}.id: the language {title} does not write `writing.field`, how a row's id is given by a "
                     "field")
    return found


SPECS = ("must be a list of {keyword}, {position} or {type_argument}: the ways a call that builds a mock names its "
         "spec, in order, such as [{keyword: spec}]")
"""What the loader says of a value of `testing.mocks.specs` that is no list of entries, or an empty one."""
_SPEC_SAID = {"keyword": "a keyword", "position": "a position", "type_argument": "a type argument"}
"""How a problem says each way a call names its spec."""


def spec_entries(value: Any, where: str, problems: list[str], language: Language) -> tuple[SpecEntry, ...] | None:
    """The ways a call that builds a mock names its spec, at least one, in the order written, each entry addressed
    `<where>.<i>`, i from 0, every entry counted, and each once; None when the list or any entry has a problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: {SPECS}")
        return None
    count = len(problems)
    found: list[SpecEntry] = []
    for index, entry in enumerate(value):
        read = _spec_entry(entry, f"{where}.{index}", problems, language)
        if read is not None and read in found:
            problems.append(f"{where}.{index}: {{{read.form}: {read.keyword or read.place}}} is listed twice")
        elif read is not None:
            found.append(read)
    return tuple(found) if len(problems) == count else None


def _spec_entry(entry: Any, where: str, problems: list[str], language: Language) -> SpecEntry | None:
    """One way a call names its spec: exactly one of {keyword: <name>}, {position: <n>} and {type_argument: <n>}."""
    form, item = next(iter(entry.items())) if isinstance(entry, Mapping) and len(entry) == 1 else ("", None)
    if form not in SPEC_FORMS:
        problems.append(f"{where}: must be one of {{keyword: <name>}}, {{position: <n>}} or {{type_argument: <n>}}")
        return None
    if form == "keyword" and not (isinstance(item, str) and names.is_name(item, language.names)):
        problems.append(f"{where}.keyword: {item!r} is not a keyword name")
        return None
    if form != "keyword" and not _counted(item):
        problems.append(f"{where}.{form}: must be a whole number, at least 0, such as 0")
        return None
    return SpecEntry(**{form: item})


def unwritten_specs(specs: tuple[SpecEntry, ...], where: str, unread: Collection[str], language: Language) -> list[str]:
    """A problem for each entry of the list at where whose way of naming a spec the language does not write (its data
    file's `writing.specs`), in the order of the list; none for an entry the needs of the profile refuse already
    (unread)."""
    writing, title = language.checked.writing, language.checked.title
    return [f"{where}.{index}: the language {title} does not write `writing.specs.{entry.form}`, how a mock is given its "
            f"spec by {_SPEC_SAID[entry.form]}" for index, entry in enumerate(specs)
            if not writing.writes_spec(entry.form) and f"{where}.{index}.{entry.form}" not in unread]


def _outside_name_at(value: Any, where: str, problems: list[str], language: Language,
                     least: int = 2) -> tuple[str, ...] | None:
    """An outside name of at least `least` steps: two by default, <package><member><name>, the path an import binds;
    one, a name the framework binds without an import too."""
    steps = _outside(value, language) if isinstance(value, str) else None
    if steps is None or len(steps) < least:
        problems.append(f"{where}: {value!r} is not an outside name such as {_such(language)}")
        return None
    return steps


def outside_names(value: Any, where: str, problems: list[str], language: Language,
                  least: int = 2) -> tuple[tuple[str, ...], ...] | None:
    """A non-empty list of outside names of at least `least` steps (see _outside_name_at), each once."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of outside names such as {_such(language)}")
        return None
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = _outside_name_at(item, where, problems, language, least)
        if steps is not None and steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        elif steps is not None:
            found.append(steps)
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
        if not isinstance(name, str) or not names.is_name(name, language.names):
            problems.append(f"{where}: {name!r} is not a parameter name")
            continue
        at = f"{where}.{name}"
        if not isinstance(spec, Mapping):
            problems.append(f"{at}: must be a mapping {{{calls}}}, and optionally autospec")
            continue
        before = len(problems)
        problems += unknown_keys(spec, {calls, "autospec"}, at, FIXTURE)
        problems += [f"{at}: missing `{calls}`"] if calls not in spec else []
        mocks = _identifiers(spec[calls], f"{at}.{calls}", problems, "method", "[build]", language) if calls in spec else None
        autospec = (_identifiers(spec["autospec"], f"{at}.autospec", problems, "method", "[build]", language)
                    if "autospec" in spec else ())
        problems += [f"{at}.autospec: {method!r} is also listed in {calls}" for method in autospec or ()
                     if mocks and method in mocks]
        if len(problems) == before and mocks is not None and autospec is not None:
            found.append(Fixture(name, mocks, autospec))
    return tuple(found) if len(problems) == count else None


def _identifiers(value: Any, where: str, problems: list[str], noun: str, example: str,
                 language: Language) -> tuple[str, ...] | None:
    """A non-empty list of names, each once, each a plain identifier: the methods of an object."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of {noun} names such as {example}")
        return None
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not names.is_name(item, language.names):
            problems.append(f"{where}: {item!r} is not a {noun} name")
        elif item in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(item)
    return tuple(found)


def _declared_forms(value: Any, where: str, problems: list[str], language: Language) -> tuple[TestForm, ...] | None:
    """The forms a test is declared in, at least one, each entry addressed `<where>.<i>`, i from 0; None when any entry
    has a problem."""
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of test forms, each {{function}} or {{call, title, body}}")
        return None
    forms = [_declared_form(entry, f"{where}.{index}", problems, language) for index, entry in enumerate(value)]
    found = tuple(form for form in forms if form is not None)
    return found if len(found) == len(forms) else None


def _declared_form(entry: Any, where: str, problems: list[str], language: Language) -> TestForm | None:
    """One form: exactly one of function and call, and only the keys of the scope."""
    if not isinstance(entry, Mapping) or sum(key in entry for key in DECLARING) != 1:
        problems.append(f"{where}: write one of function, call")
        return None
    count = len(problems)
    problems += unknown_keys(entry, names_of(DECLARED), where, DECLARED)
    if "function" in entry:
        return _function_form(entry, where, problems, language, count)
    return _call_form(entry, where, problems, language, count)


def _function_form(entry: Mapping[Any, Any], where: str, problems: list[str], language: Language,
                   count: int) -> TestForm | None:
    """A function form: a name pattern, `*` for any text, and no slot of a call form; count is how many problems
    there were before the entry."""
    problems += [f"{where}.{slot}: a function form takes no slot: drop {slot}" for slot in CALL_SLOTS if slot in entry]
    pattern = entry["function"]
    if not (isinstance(pattern, str) and names.is_name(pattern.replace("*", "x"), language.names)):
        problems.append(f"{where}.function: must be a function name pattern: a name with `*` for any text")
    return TestForm(function=pattern) if len(problems) == count else None


def _call_form(entry: Mapping[Any, Any], where: str, problems: list[str], language: Language,
               count: int) -> TestForm | None:
    """A call form: at least one callee, each a name of one step or more, and the places of the test's title and its
    body among the call's arguments; count is how many problems there were before the entry."""
    problems += [f"{where}: missing `{slot}`" for slot in CALL_SLOTS if slot not in entry]
    if entry["call"] == []:
        problems.append(f"{where}.call: must list at least one callee")
    calls = outside_names(entry["call"], f"{where}.call", problems, language, 1) if entry["call"] != [] else None
    title = _place(entry["title"], f"{where}.title", problems, language) if "title" in entry else None
    body = _place(entry["body"], f"{where}.body", problems, language) if "body" in entry else None
    if len(problems) != count or calls is None or title is None or body is None:
        return None
    return TestForm(call=calls, title=title, body=body)


def framework_patterns(value: Any, problems: list[str], where: str, known: Collection[str],
                       language: Language, scope: str = "") -> Framework | None:
    """How the test framework names test files and declares its tests, the map written at `where`; `known` are the
    keys the map may hold, which the caller may widen with what it reads itself, and `scope` the scope whose retired
    names the map's unknown keys are looked up in."""
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping {{files, declared}}: the patterns of a test file's name and the "
                        "forms that declare a test")
        return None
    count = len(problems)
    problems += unknown_keys(value, known, where, scope)
    problems += [f"{where}: missing `{key}`" for key in ("files", "declared") if key not in value]
    files = _file_patterns(value["files"], problems, f"{where}.files", language) if "files" in value else None
    skips = outside_names(value["skips"], f"{where}.skips", problems, language) if "skips" in value else ()
    declared = _declared_forms(value["declared"], f"{where}.declared", problems, language) if "declared" in value else None
    bound = outside_names(value["globals"], f"{where}.globals", problems, language, 1) if "globals" in value else ()
    if len(problems) != count or files is None or skips is None or declared is None or bound is None:
        return None
    return Framework(files, declared, skips, globals=bound)


def _file_patterns(value: Any, problems: list[str], where: str, language: Language) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of file name patterns, each a {endings(language)} name "
                        "with `*` for any text")
        return None
    pattern = _file_pattern(language)
    found: list[str] = []
    for item in value:
        if not isinstance(item, str) or not pattern.fullmatch(item):
            problems.append(f"{where}: {item!r} is not a file name pattern: a name ending in {endings(language)}, "
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
        if not names.is_name(name, language.names):
            problems.append(f"{where}: {name!r} is not a name a parameter can have")
        elif name in value[:i]:
            problems.append(f"{where}: {name!r} is listed twice")
    return (value[0], value[1], value[2]) if len(problems) == count else None


def unknown_keys(spec: Mapping[Any, Any], known: Collection[str], where: str, scope: str = "") -> list[str]:
    """The problems of the keys of the mapping at where that are not known (see unknown_of), each naming where."""
    return [f"{where}: {problem}" for problem in unknown_of(spec, known, scope)]


def unknown_of(spec: Mapping[Any, Any], known: Collection[str], scope: str = "") -> list[str]:
    """The problems of the keys of a mapping that are not known, as the top of the file, which has no address, says
    them: one of its own for each that the table of retired names holds under the scope, in sorted order, then one for
    all the others; a scope of "" reads no entry."""
    unknown = sorted(str(k) for k in spec if k not in known)
    problems = [f"unknown key {quoted([name])}: {advice(scope, name, known)}" for name in unknown if retired(scope, name)]
    rest = [name for name in unknown if not retired(scope, name)]
    if rest:
        problems.append(f"unknown key{'s' if len(rest) > 1 else ''} {quoted(rest)}: use {', '.join(sorted(known))}")
    return problems


def advice(scope: str, name: str, known: Collection[str]) -> str:
    """What a name that is not known is told: the fixed text of its entry in the table of retired names under the
    scope, when it has one, then the names that are, sorted."""
    text = retired(scope, name)
    return f"{text}; use {', '.join(sorted(known))}" if text else f"use {', '.join(sorted(known))}"


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
        if not _is_package(name, language):
            problems.append(f"reserved: {name!r} is not a package name the language {language.checked.title} allows")
        elif name not in language.standard_names:
            problems.append(f"reserved: {name!r} is not in the {language.checked.title} standard library: an outside package "
                            "is imported only by the parts whose `imports.libraries` list it already")
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
        if not _is_package(package, language):
            problems.append(f"{where}: {package!r} is not a package name the language {language.checked.title} allows")
        elif package in language.standard_names and package not in reserved:
            problems.append(f"{where}: {package!r} is in the standard library, which every part may import unless "
                            "`reserved` names it")
        elif package in found:
            problems.append(f"{where}: {package!r} is listed twice")
        else:
            found.append(package)
    return tuple(found)


def never_names(value: Any, where: str, problems: list[str],
                language: Language) -> tuple[tuple[str, ...] | None, ...] | None:
    """The names a part may not use, one for each item in its place, None for an item refused: outside names,
    <package><member><name>, or packages alone, read by the language's patterns; a builtin is written in the language's
    namespace for them, <namespace><member><name>. A method called on anything is written `.<name>()` and kept as
    written, split at its dot: ("", "<name>()")."""
    member = language.checked.member
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a non-empty list of outside names, packages or methods, such as "
                        f"[{_such(language)}, <package>, .<name>()]")
        return None
    found: list[tuple[str, ...]] = []
    read: list[tuple[str, ...] | None] = []
    for item in value:
        count = len(problems)
        method = _method_name(item, language) if isinstance(item, str) else None
        steps = (("", f"{method}{CALLED}") if method is not None
                 else _outside(item, language, language.namespace) if isinstance(item, str) else None)
        if method is not None and language.checked.is_special(method):
            problems.append(f"{where}: {item!r} is a special method, which no code calls by name")
        elif method is None and isinstance(item, str) and item.startswith(".") and names.is_name(item[1:], language.names):
            problems.append(f"{where}: {item!r} is neither an outside name nor a method: write {item}() for a method "
                            "called on anything")
        elif steps is None:
            problems.append(f"{where}: {item!r} is not an outside name such as {_such(language)}, nor a package, nor a "
                            "method such as .<name>()")
        elif len(steps) == 1 and item in language.builtin_names:
            problems.append(f"{where}: {item!r} is a {language.checked.title} builtin, which a bare name does not ban: "
                            f"write {language.namespace}{member}{item}")
        elif steps in found:
            problems.append(f"{where}: {item!r} is listed twice")
        else:
            found.append(steps)
        read.append(steps if len(problems) == count else None)
    return tuple(read)


def scenario_places(results: Any, tier: Any, suffix: Any, parts: dict[str, Part], declared: set[str],
                    tiers: tuple[Tier, ...], where: str, problems: list[str], language: Language, *,
                    words: Collection[str]) -> None:
    """The part holding the result unions lies in a repeating folder, the tier is declared and tests that part, and the
    suffix is the end of a name."""
    part = parts.get(results) if isinstance(results, str) else None
    if part is None:
        if (prefixed := outside_imports(results, declared, words)) is not None:
            problems.append(f"{where}.results: {prefixed}")
        elif not isinstance(results, str) or results not in declared:
            problems.append(f"{where}.results: no part named {results!r}")
    elif not part.in_instance:
        problems.append(f"{where}.results: part '{results}' does not lie in the repeating folder: its unions are "
                        "matched to the tests of the same folder")
    found = next((t for t in tiers if t.name == tier), None)
    if found is None:
        problems.append(f"{where}.tier: no tier named {tier!r}")
    elif part is not None and not any(item.part == results for item in found.subject):
        problems.append(f"{where}.tier: tier '{tier}' does not test part '{results}'")
    if not isinstance(suffix, str) or not names.is_name(suffix, language.names):
        problems.append(f"{where}.suffix: must be the end of a name, such as Result")
