"""What a copy of a profile is called and changes in its document, where it goes, and how the project records it."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.values import PROFILE_SUFFIX

DEFAULT_FOLDER = "architecture"
"""Where a new profile goes by default, below the folder holding the app folder: in a folder of its own, named for it."""
_VALID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def valid_name(name: str) -> bool:
    """Whether a profile can be called name: it names the copy's folder and file."""
    return _VALID.fullmatch(name) is not None


def recorded(profile: Path, root: Path, cwd: Path) -> str:
    """The profile file as pyproject.toml, in root, records it: relative to root, written with `/`; a relative profile
    or root is read from cwd."""
    return Path(os.path.relpath(cwd / profile, cwd / root)).as_posix()


def copied_document(document: Any, name: str, based_on: str) -> Any:
    """The document of the copy, as its text is renamed: named name, and based on based_on."""
    return {**document, "name": name, "based_on": based_on}


def project_root(app: Path) -> Path:
    """The folder holding the app folder: the project's, where pyproject.toml records a profile and a copy goes."""
    return app.parent


def copy_file(name: str) -> str:
    """The name of the profile file of a copy called name."""
    return f"{name}{PROFILE_SUFFIX}"


def copy_folder(root: Path, name: str, out: Path | None) -> Path:
    """Where the copy goes: out, else a folder named for it below the default folder in root."""
    return out if out is not None else root / DEFAULT_FOLDER / name
