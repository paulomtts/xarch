"""How a command shows why it refuses: the reason as one line of text, or as the JSON document {"ok": false,
"error"}; a profile that cannot be chosen, and one whose own checks cannot run, said in words."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from xarch.cli.reports.document import document
from xarch.cli.reports.shown import shown
from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused


def reason(refused: NoProfileChosen | ProfileRefused) -> str:
    """Why spec chose no profile: none is given or configured, said with how to choose one, or its own reason."""
    match refused:
        case NoProfileChosen(known):
            return _no_profile(known)
        case ProfileRefused(why):
            return why


def _no_profile(known: Sequence[str], how: str = "pass --profile") -> str:
    """Why nothing can run without a profile, and how to choose one: how the command is given one, or the setting."""
    return (f"no profile: {how}, or set `profile` under [tool.xarch] in pyproject.toml; "
            f"the profiles found are {', '.join(known)}")


def no_profile_to_check(known: Sequence[str]) -> str:
    """Why `profile check` has no profile to check, and how to give it one: by name or path, as its argument."""
    return _no_profile(known, "name one as its argument, a bundled name or a path to a profile file")


def cannot_run(problems: Sequence[str]) -> str:
    """Why a profile whose own checks cannot run is refused, and how to see every problem."""
    return ("the checks the profile writes itself cannot run (`xarch profile check` says the same):\n"
            + "\n".join(f"  {problem}" for problem in problems))


def not_a_directory(root: Path, cwd: Path) -> str:
    """Why a folder to check is refused: it is no folder, shown from the working folder when it lies below it."""
    return f"{shown(root, cwd)} is not a directory"


def rule_needs_key() -> str:
    """Why `profile explain --rule` is refused without a key, or with --configured."""
    return "--rule shows the rules of a key: give a key, such as parts.names, and --profile or a configured profile"


def key_or_profile() -> str:
    """Why `profile explain` is refused a key and a profile at once, or both kinds of profile."""
    return "give either a key or a profile (--profile or --configured), not both"


def text_error(why: str) -> str:
    return f"error: {why}"


def json_error(why: str) -> str:
    return document({"ok": False, "error": why})
