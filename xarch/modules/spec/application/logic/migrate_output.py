"""Where a conversion from format 1 goes, and which documents it refuses to convert."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.values import PROFILE_SUFFIX

SUFFIX = "-v2"
"""What the folder of a conversion made without `--out` adds to the name of the file."""


def converted_name(path: Path) -> str:
    """The name of the converted profile in its folder: the old file's, as a profile file xarch writes."""
    return f"{path.stem}{PROFILE_SUFFIX}"


def converted_folder(path: Path, out: Path | None) -> Path:
    """Where the conversion goes: out, else a folder beside the old file named for it with SUFFIX."""
    return out if out is not None else path.parent / f"{path.stem}{SUFFIX}"


def not_format_1(document: Any, location: str) -> str | None:
    """Why the document is no profile of format 1 to convert, or None when it is one."""
    version = document.get("xarch") if isinstance(document, dict) else None
    if version == 1 and type(version) is int:
        return None
    if version == 2 and type(version) is int:
        return f"{location}: already in format 2: nothing to migrate"
    said = f"it says `xarch: {version}`" if isinstance(document, dict) and "xarch" in document else "it has no `xarch`"
    return f"{location}: not a profile of format 1: {said}"
