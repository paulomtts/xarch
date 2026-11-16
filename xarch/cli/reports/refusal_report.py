"""How a command shows why it refuses: the reason as one line of text, or as the JSON document {"ok": false,
"error"}; a profile that cannot be chosen, and one whose own checks cannot run, said in words."""
from __future__ import annotations

import json
from collections.abc import Sequence

from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused


def reason(refused: NoProfileChosen | ProfileRefused) -> str:
    """Why spec chose no profile: none is given or configured, said with how to choose one, or its own reason."""
    match refused:
        case NoProfileChosen(known):
            return no_profile(known)
        case ProfileRefused(why):
            return why


def no_profile(known: Sequence[str]) -> str:
    """Why nothing can run without a profile, and how to choose one."""
    return ("no profile: pass --profile, or set `profile` under [tool.xarch] in pyproject.toml; "
            f"the profiles found are {', '.join(known)}")


def cannot_run(problems: Sequence[str]) -> str:
    """Why a profile whose own checks cannot run is refused, and how to see every problem."""
    return ("the checks the profile writes itself cannot run (`xarch profile check` says the same):\n"
            + "\n".join(f"  {problem}" for problem in problems))


def text_error(why: str) -> str:
    return f"error: {why}"


def json_error(why: str) -> str:
    return json.dumps({"ok": False, "error": why}, indent=2, ensure_ascii=False)
