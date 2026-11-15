"""The data file of a language (`presets/language/<name>.yaml`): what is true of the language as a whole and is needed
outside the reader that turns source into facts. Read into a Language, with every problem listed; the names only the
runtime knows are added to it by the service that holds the runtime.

    title          how a message names the language
    extension      the ending of a source file's name: a dot and a name
    package_file   the name of the file that stands for the folder holding it, ending in the extension
    interface      dotted names, any of which among a class's bases marks it as an interface
    dynamic        dotted names of what imports by a name worked out when the code runs; optional
    namespace      the namespace of the names the language binds without an import
    cache          the folder in which its tools keep what they compile, which no check or example reads; optional
    standard       where the names of the standard library are known from
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Language

FOLDER = "presets/language"
"""Where the data files of the languages are, below the bundled folder: one YAML file each, named for the language."""
KEYS = ("title", "extension", "package_file", "interface", "dynamic", "namespace", "cache", "standard")
REQUIRED = ("title", "extension", "package_file", "namespace", "standard")
_EXTENSION = re.compile(r"\.[A-Za-z0-9]+")
_DOTTED = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_FOLDER = re.compile(r"[A-Za-z0-9_.-]+")


def language_of(name: str, document: Any) -> Language:
    """The language the document of the preset called name describes; raises InvalidArchitecture."""
    source = f"{FOLDER}/{name}.yaml"
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, ["must be a mapping of keys, such as title, extension and package_file"])
    problems: list[str] = []
    unknown = sorted(str(key) for key in document if key not in KEYS)
    if unknown:
        problems.append(f"unknown key{'s' if len(unknown) > 1 else ''} {', '.join(f'{key!r}' for key in unknown)}: "
                        f"use {', '.join(sorted(KEYS))}")
    problems += [f"missing `{key}`" for key in REQUIRED if key not in document]
    title = _text(document, "title", "must be a non-empty string", problems)
    extension = _text(document, "extension", "must be a dot and a name, such as .pas", problems, _EXTENSION)
    package_file = _text(document, "package_file", "must be a file name ending in the extension", problems)
    if package_file and not (extension and package_file.endswith(extension) and package_file != extension):
        problems.append("package_file: must be a file name ending in the extension")
    interface = _dotted(document, "interface", problems)
    dynamic = _dotted(document, "dynamic", problems)
    namespace = _text(document, "namespace", "must be a name", problems, _WORD)
    standard = _text(document, "standard", "must be a name", problems, _WORD)
    cache = _text(document, "cache", "must be a folder name", problems, _FOLDER)
    if problems:
        raise InvalidArchitecture(source, problems)
    return Language(name, title, extension, package_file, interface, dynamic, namespace, standard, cache)


def _text(document: Mapping[Any, Any], key: str, said: str, problems: list[str],
          pattern: re.Pattern[str] | None = None) -> str:
    if key not in document:
        return ""
    value = document[key]
    if not isinstance(value, str) or not value.strip() or (pattern is not None and not pattern.fullmatch(value)):
        problems.append(f"{key}: {said}")
        return ""
    return value


def _dotted(document: Mapping[Any, Any], key: str, problems: list[str]) -> tuple[tuple[str, ...], ...]:
    if key not in document:
        return ()
    value = document[key]
    if not isinstance(value, list):
        problems.append(f"{key}: must be a list of dotted names, such as [pkg.Name]")
        return ()
    found: list[tuple[str, ...]] = []
    for item in value:
        if not isinstance(item, str) or not _DOTTED.fullmatch(item):
            problems.append(f"{key}: {item!r} is not a dotted name such as pkg.name")
        else:
            found.append(tuple(item.split(".")))
    return tuple(found)
