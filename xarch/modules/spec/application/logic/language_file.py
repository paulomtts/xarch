"""The data file of a language (`presets/language/<name>.yaml`): what is true of the language as a whole and is needed
outside the reader that turns source into facts. Read into a Language, with every problem listed; the names only the
runtime knows are added to it by the service that holds the runtime.

    title          how a message names the language
    extension      the ending of a source file's name: a dot and a name
    package_file   the name of the file that stands for the folder holding it, ending in the extension
    interface      outside names (see below), any of which among a class's bases marks it as an interface
    dynamic        outside names of what imports by a name worked out when the code runs; optional
    namespace      the namespace of the names the language binds without an import: a name
    cache          the folder in which its tools keep what they compile, left out of the examples, of a copy of a
                   profile and of the files init writes; optional
    standard       where the names of the standard library are known from

and, all optional, the tokens of its code the checks and the docs need (empty: the language has none):

    name           a regular expression: what a name may be
    package        a regular expression: what an import names from outside the app as one step
    member         the text that joins a package to a name in it in a profile's lists; name, package and member
                   are given together, and an outside name is written <package> or <package><member><name>, more
                   names after the first joined by `.`. Left out together, any text is a name and an outside name is
                   its whole text
    private        what a name private to its file or folder starts with
    special        what a name the language reserves for itself starts and ends with
    call           the special method that calling an instance runs
    nothing        the return annotation of a function that gives no value
    comment        the marker of a line comment
    directives     the comments its tools read as instructions, each after the marker; a space stands for any spaces
    shebang        how line 1 names the program that runs the file
    encoding       a regular expression: how line 1 or 2 declares the file's encoding, after the marker
    branching      the keywords of the statements that branch
    branching_expressions
                   the keywords of the expressions that choose between values, as its reader records them
    immutable      what makes a class an immutable record: each an outside name among its bases or its decorators,
                   a decorator's written with the keywords it must be called with, `name(key=value, ...)`
    importing      how a file imports a name from another file of the app: {dotted} stands for that file's dotted
                   path, {name} for the name

and the facts its reader supplies (see capabilities), each graded:

    supplies       {<fact>: exact | {partial: <what it misses>}}: a fact it does not list it does not supply, so a
                   key whose check needs one is refused; a partial one is listed as approximate where it is read.
                   Left out, the file does not say what a reader supplies (no reader is written for it yet), and
                   no key is held to it
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from xarch.kernel.logic.names import is_name, outside_name
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import LANGUAGES, Language
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
from xarch.profile_values.language import CheckedLanguage, RecordMark

KEYS = ("title", "extension", "package_file", "interface", "dynamic", "namespace", "cache", "standard", "name", "package",
        "member", "private", "special", "call", "nothing", "comment", "directives", "shebang", "encoding", "branching",
        "importing", "supplies", "immutable", "branching_expressions")
REQUIRED = ("title", "extension", "package_file", "namespace", "standard")
JOINED = ("name", "package", "member")
"""The keys that say how an outside name is written: given together or not at all."""
_EXTENSION = re.compile(r"\.[A-Za-z0-9]+")
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PARTIAL = "partial"
"""How the data file grades a fact its reader supplies only partly, with what it misses."""
_FOLDER = re.compile(r"[A-Za-z0-9_.-]+")
_IMPORTING = re.compile(r"(?=[^\n]*\{dotted\})(?=[^\n]*\{name\})[^\n]+")
_MEMBER = re.compile(r"\S+")
_CALLED = re.compile(r"(?P<path>[^()]+)(?:\((?P<keywords>[^()]*)\))?")
_VALUE = re.compile(r"[^,()=]+")


def language_of(name: str, document: Any) -> Language:
    """The language the document of the preset called name describes; raises InvalidArchitecture."""
    source = f"{LANGUAGES}/{name}.yaml"
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys, such as title, extension and package_file"])
    problems: list[str] = []
    unknown = sorted(str(key) for key in document if key not in KEYS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {', '.join(f'{key!r}' for key in unknown)}: "
                        f"use {', '.join(sorted(KEYS))}")
    problems += [f"missing `{key}`" for key in REQUIRED if key not in document]
    joins = _joins(document, problems)
    names, package, member = joins or ("", "", "")
    title = _text(document, "title", "must be a non-empty string", problems)
    extension = _text(document, "extension", "must be a dot and a name, such as .pas", problems, _EXTENSION)
    package_file = _text(document, "package_file", "must be a file name ending in the extension", problems)
    if package_file and not (extension and package_file.endswith(extension) and package_file != extension):
        problems.append("package_file: must be a file name ending in the extension")
    namespace = _text(document, "namespace", "must be a name", problems)
    if namespace and not is_name(namespace, names):
        problems.append("namespace: must be a name")
        namespace = ""
    interface = _outside(document, "interface", problems, joins, namespace)
    dynamic = _outside(document, "dynamic", problems, joins, namespace)
    standard = _text(document, "standard", "must be a name", problems, _WORD)
    cache = _text(document, "cache", "must be a folder name", problems, _FOLDER)
    tokens = {key: _text(document, key, "must be a non-empty string", problems)
              for key in ("private", "special", "call", "nothing", "comment", "shebang")}
    encoding = _pattern(document, "encoding", problems)
    directives = _words(document, "directives", problems)
    branching = _words(document, "branching", problems)
    expressions = _words(document, "branching_expressions", problems)
    importing = _text(document, "importing", "must be a line holding {dotted} and {name}", problems, _IMPORTING)
    supplies = _supplies(document["supplies"], problems) if "supplies" in document else None
    immutable = _marks(document, problems, joins, namespace)
    if problems:
        raise InvalidArchitecture(source, problems)
    checked = CheckedLanguage(title, extension, package_file, interface, dynamic, tokens["private"], tokens["special"],
                              tokens["call"], tokens["nothing"], tokens["comment"], directives, tokens["shebang"],
                              encoding, branching, supplies, importing, immutable, expressions, names, package, member)
    return Language(name, checked, namespace, standard, cache, names)


def _joins(document: Mapping[Any, Any], problems: list[str]) -> tuple[str, str, str] | None:
    """The pattern of a name, the pattern of a package and the member that joins a name to it: ("", "", "") when the
    document gives none of them, None when it gives one wrong or not all three."""
    count = len(problems)
    names = _pattern(document, "name", problems)
    package = _pattern(document, "package", problems)
    member = _text(document, "member", "must be a non-empty string with no space", problems, _MEMBER)
    if any(key in document for key in JOINED):
        problems += [f"missing `{key}`: name, package and member are given together" for key in JOINED
                     if key not in document]
    return (names, package, member) if len(problems) == count else None


def _outside(document: Mapping[Any, Any], key: str, problems: list[str], joins: tuple[str, str, str] | None,
             namespace: str) -> tuple[tuple[str, ...], ...]:
    """The outside names listed at key, each as its steps; none read when the keys that say how one is written are
    refused already (joins None)."""
    if key not in document or joins is None:
        return ()
    names, package, member = joins
    such = f"<package>{member}<name>"
    value = document[key]
    if not isinstance(value, list):
        problems.append(f"{key}: must be a list of outside names, such as [{such}]")
        return ()
    found: list[tuple[str, ...]] = []
    for item in value:
        steps = outside_name(item, names, package, member, namespace) if isinstance(item, str) else None
        if steps is None:
            problems.append(f"{key}: {item!r} is not an outside name such as {such}")
        else:
            found.append(steps)
    return tuple(found)


def _marks(document: Mapping[Any, Any], problems: list[str], joins: tuple[str, str, str] | None,
           namespace: str) -> tuple[RecordMark, ...]:
    if "immutable" not in document or joins is None:
        return ()
    such = f"<package>{joins[2]}<name>"
    value = document["immutable"]
    if not isinstance(value, list):
        problems.append(f"immutable: must be a list of outside names, each perhaps called with keywords, such as "
                        f"[{such}, \"{such}(<name>=<value>)\"]")
        return ()
    found: list[RecordMark] = []
    for item in value:
        mark = _mark(item, joins, namespace) if isinstance(item, str) else None
        if mark is None:
            problems.append(f"immutable: {item!r} is not an outside name such as {such}, or one called with keywords "
                            f"such as {such}(<name>=<value>)")
        else:
            found.append(mark)
    return tuple(found)


def _mark(item: str, joins: tuple[str, str, str], namespace: str) -> RecordMark | None:
    """One mark of an immutable record: an outside name, perhaps called with keywords, `name(key=value, ...)`, each key a
    name of the language and each value plain text; None when the text is none."""
    names, package, member = joins
    called = _CALLED.fullmatch(item)
    path = outside_name(called["path"], names, package, member, namespace) if called is not None else None
    if called is None or path is None:
        return None
    if called["keywords"] is None:
        return RecordMark(path)
    pairs = [pair.partition("=") for pair in called["keywords"].split(",")]
    if not all(sep and is_name(key.strip(), names) and _VALUE.fullmatch(value.strip()) for key, sep, value in pairs):
        return None
    return RecordMark(path, tuple((key.strip(), value.strip()) for key, _, value in pairs))


def _text(document: Mapping[Any, Any], key: str, said: str, problems: list[str],
          pattern: re.Pattern[str] | None = None) -> str:
    if key not in document:
        return ""
    value = document[key]
    if not isinstance(value, str) or not value.strip() or (pattern is not None and not pattern.fullmatch(value)):
        problems.append(f"{key}: {said}")
        return ""
    return value


def _pattern(document: Mapping[Any, Any], key: str, problems: list[str]) -> str:
    value = _text(document, key, "must be a regular expression", problems)
    try:
        re.compile(value)
    except re.error as e:
        problems.append(f"{key}: must be a regular expression: {e}")
        return ""
    return value


def _words(document: Mapping[Any, Any], key: str, problems: list[str]) -> tuple[str, ...]:
    if key not in document:
        return ()
    value = document[key]
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        problems.append(f"{key}: must be a list of non-empty strings")
        return ()
    return tuple(value)


def _supplies(value: Any, problems: list[str]) -> tuple[Supply, ...]:
    if not isinstance(value, Mapping):
        problems.append(f"supplies: must be a mapping of facts to {EXACT} or {{{PARTIAL}: <what it misses>}}")
        return ()
    found: dict[str, Supply] = {}
    for fact, grade in value.items():
        if fact not in FACTS:
            problems.append(f"supplies: {fact!r} is not a fact a check reads: use {', '.join(sorted(FACTS))}")
        elif grade == EXACT:
            found[fact] = Supply(fact, EXACT)
        elif isinstance(grade, Mapping) and list(grade) == [PARTIAL] and isinstance(grade[PARTIAL], str) \
                and grade[PARTIAL].strip():
            found[fact] = Supply(fact, PARTIAL, grade[PARTIAL])
        else:
            problems.append(f"supplies.{fact}: must be {EXACT}, or {{{PARTIAL}: <what it misses>}} with a line of text")
    return tuple(found.values())


def first_language(languages: Iterable[str]) -> str:
    """The language of an app whose profile names none: the first of the languages xarch reads, by name; "" when it
    reads none."""
    return min(languages, default="")
