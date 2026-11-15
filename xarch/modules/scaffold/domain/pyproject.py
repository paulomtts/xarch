"""Recording the settings xarch reads in a pyproject.toml's [tool.xarch] table (the profile in force and, when it is not
the default, the app folder), as text, never rewriting a value.

A location that is a path (it has a folder or a suffix) is recorded relative to the folder holding the pyproject.toml,
which is how xarch reads it back; a bundled name is recorded as it is. The app folder is recorded the same way, as a
posix path relative to the folder holding the pyproject.toml.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

TABLE = "[tool.xarch]"
DEFAULT_APP = "app"
"""The app folder xarch assumes, beside the pyproject.toml, when none is given or recorded."""
_HEADER = re.compile(r"\s*\[")


def recorded_location(location: str, folder: Path) -> str:
    """The location as the pyproject.toml in folder records it."""
    path = Path(location)
    if len(path.parts) == 1 and not path.suffix:
        return location
    return Path(os.path.relpath(path.absolute(), folder.absolute())).as_posix()


def recorded_app(app: Path, folder: Path) -> str | None:
    """The app folder as the pyproject.toml in folder records it: relative to it, as posix; None for the default
    folder, which needs no record."""
    shown = Path(os.path.relpath(app.absolute(), folder.absolute())).as_posix()
    return None if shown == DEFAULT_APP else shown


def with_profile(text: str | None, location: str) -> str | None:
    """The text with `profile = "<location>"` in its [tool.xarch] table, or None if the table already sets one or
    the file defines the table in a way this cannot extend safely."""
    return with_setting(text, "profile", location)


def with_setting(text: str | None, key: str, value: str, after: str | None = None) -> str | None:
    """The text with `<key> = "<value>"` in its [tool.xarch] table, the table added when there is none: right after the
    line of the key `after` when the table holds it, else at the top; None if the table already sets the key or the
    file defines the table in a way this cannot extend safely."""
    line = f"{key} = {_quoted(value)}\n"
    if text is None or not text.strip():
        return f"{TABLE}\n{line}"
    lines = text.splitlines(keepends=True)
    headers = [i for i, raw in enumerate(lines) if raw.strip() == TABLE]
    if not headers:
        if re.search(r"^\s*(tool\s*\.\s*xarch|xarch)\b", text, re.MULTILINE):
            return None
        return text.rstrip("\n") + f"\n\n{TABLE}\n{line}"
    start = headers[0] + 1
    end = next((i for i in range(start, len(lines)) if _HEADER.match(lines[i])), len(lines))
    if any(re.match(rf"\s*{re.escape(key)}\s*=", raw) for raw in lines[start:end]):
        return None
    anchor = next((i + 1 for i in range(start, end) if after is not None
                   and re.match(rf"\s*{re.escape(after)}\s*=", lines[i])), start)
    return "".join(lines[:anchor] + [line] + lines[anchor:])


def _quoted(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
