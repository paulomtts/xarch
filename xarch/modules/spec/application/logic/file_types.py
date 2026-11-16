"""The data file of the kinds of file the docs quote besides the language of the app (`presets/format/file_types.yaml`),
read into a FileType by each ending, with every problem listed:

    <ending>    a dot and a name, such as .sql: {fence, comment}, one of them at least
        fence   the word that names the language of a fenced block of such files; left out, the ending without its dot
        comment the marker of a line comment in them; left out, the one of the language of the app
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import FILE_TYPES, FileType

FIELDS = ("fence", "comment")
_ENDING = re.compile(r"\.[A-Za-z0-9]+")


def file_types_of(document: Any) -> dict[str, FileType]:
    """What the document of the data file says of each kind of file, by its ending; raises InvalidArchitecture listing
    every problem."""
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(FILE_TYPES, ["must be a mapping of endings, such as .sql, to {fence, comment}"])
    problems: list[str] = []
    found: dict[str, FileType] = {}
    for ending, entry in document.items():
        if not isinstance(ending, str) or not _ENDING.fullmatch(ending):
            problems.append(f"{ending}: must be a dot and a name, such as .sql")
        elif not isinstance(entry, Mapping) or not entry:
            problems.append(f"{ending}: must be a mapping of {', '.join(FIELDS)}, one of them at least")
        else:
            found[ending] = _file_type(ending, entry, problems)
    if problems:
        raise InvalidArchitecture(FILE_TYPES, problems)
    return found


def _file_type(ending: str, entry: Mapping[Any, Any], problems: list[str]) -> FileType:
    unknown = sorted(str(field) for field in entry if field not in FIELDS)
    if unknown:
        problems.append(f"{ending}: unknown key{'s' if len(unknown) > 1 else ''} "
                        f"{', '.join(repr(field) for field in unknown)}: use {', '.join(FIELDS)}")
    empty = [field for field in FIELDS if field in entry and (not isinstance(entry[field], str) or not entry[field].strip())]
    problems += [f"{ending}.{field}: must be a non-empty string" for field in empty]
    return FileType(*(str(entry.get(field, "")) for field in FIELDS))
