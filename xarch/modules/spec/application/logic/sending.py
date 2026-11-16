"""What `review` says of what review may send: the files it never sends (`review.never`, path patterns below the app)
and the texts it hides before it sends (`review.mask`, text patterns), each refused at its address when it is written
wrong. `check` reads neither."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.domain.profile_keys import REVIEW

ANY_STEP, ANY_FOLDERS = "*", "**"
"""In a path pattern: any text inside one step, and, as a whole step, any number of folders."""
_NOT_A_PATH = ("is not a path below the app: write its steps with /, * for any text inside one step and ** for any "
               "number of folders, such as documents/drafts")


def sending(value: Any, problems: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The path patterns review never sends and the text patterns it hides, each in the order of the file."""
    if not isinstance(value, Mapping):
        problems.append("review: must be a mapping {never, mask}: the files review never sends and the texts it hides "
                        "before it sends")
        return (), ()
    problems += ck.unknown_keys(value, names_of(REVIEW), "review")
    never = _never(value["never"], problems) if "never" in value else ()
    mask = _mask(value["mask"], problems) if "mask" in value else ()
    return never, mask


def _never(value: Any, problems: list[str]) -> tuple[str, ...]:
    where = "review.never"
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of paths below the app, such as [documents/drafts, '**/secrets']")
        return ()
    found: list[str] = []
    for entry in value:
        steps = entry.split("/") if ck.line(entry) and not entry.startswith("/") else []
        if not steps or any(step in ("", ".", "..") for step in steps):
            problems.append(f"{where}: {entry!r} {_NOT_A_PATH}")
        elif any(ANY_FOLDERS in step and step != ANY_FOLDERS for step in steps):
            problems.append(f"{where}: {entry!r}: ** stands alone as a step, for any number of folders")
        elif all(set(step) == {ANY_STEP} for step in steps):
            problems.append(f"{where}: {entry!r} holds back every file: name the files or folders review must not "
                            "send")
        elif entry in found:
            problems.append(f"{where}: {entry!r} is listed twice")
        else:
            found.append(entry)
    return tuple(found)


def _mask(value: Any, problems: list[str]) -> tuple[str, ...]:
    where = "review.mask"
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of texts to hide before review sends, such as [Northwind, 'DOC-*']")
        return ()
    found: list[str] = []
    for entry in value:
        if not ck.line(entry):
            problems.append(f"{where}: {entry!r} is not a text to hide: write one line of text, * for any run of "
                            "letters, digits, _, - and .")
        elif not entry.replace(ANY_STEP, "").strip():
            problems.append(f"{where}: {entry!r} would hide every word: write the text around the *")
        elif entry in found:
            problems.append(f"{where}: {entry!r} is listed twice")
        else:
            found.append(entry)
    return tuple(found)
