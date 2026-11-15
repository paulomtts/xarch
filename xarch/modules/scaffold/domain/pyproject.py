"""Recording the architecture in force in a pyproject.toml's [tool.xarch] table, as text, never rewriting a value.

A location that is a path (it has a folder or a suffix) is recorded relative to the folder holding the pyproject.toml,
which is how xarch reads it back; a bundled name is recorded as it is.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

TABLE = "[tool.xarch]"
_KEY = re.compile(r"\s*profile\s*=")
_HEADER = re.compile(r"\s*\[")


def recorded_location(location: str, folder: Path) -> str:
    """The location as the pyproject.toml in folder records it."""
    path = Path(location)
    if len(path.parts) == 1 and not path.suffix:
        return location
    return Path(os.path.relpath(path.absolute(), folder.absolute())).as_posix()


def with_profile(text: str | None, location: str) -> str | None:
    """The text with `profile = "<location>"` in its [tool.xarch] table, or None if the table already sets one or
    the file defines the table in a way this cannot extend safely."""
    line = f'profile = "{location}"\n'
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
    if any(_KEY.match(raw) for raw in lines[start:end]):
        return None
    return "".join(lines[:start] + [line] + lines[start:])
