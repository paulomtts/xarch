"""What a copy of a profile changes in its text, and how the project records it."""
from __future__ import annotations

import os
import re
from pathlib import Path

_NAME = re.compile(r"^name:.*$", re.MULTILINE)
_BASED_ON = re.compile(r"^based_on:.*\n", re.MULTILINE)
_VALID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def valid_name(name: str) -> bool:
    """Whether a profile can be called name: it names the copy's folder and file."""
    return _VALID.fullmatch(name) is not None


def copied_text(text: str, name: str, based_on: str) -> str | None:
    """The text with its `name` set to name and `based_on` to based_on, right after it, every other line, comment
    included, as written; None when the text has no top-level `name` line."""
    without = _BASED_ON.sub("", text)
    if _NAME.search(without) is None:
        return None
    return _NAME.sub(lambda _: f"name: {name}\nbased_on: {based_on}", without, count=1)


def recorded(profile: Path, root: Path, cwd: Path) -> str:
    """The profile file as pyproject.toml, in root, records it: relative to root, written with `/`; a relative profile
    or root is read from cwd."""
    return Path(os.path.relpath(cwd / profile, cwd / root)).as_posix()
