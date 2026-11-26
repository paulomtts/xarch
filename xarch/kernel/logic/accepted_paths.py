"""How an entry of an accepted list (checks.<id>.accepted, structure.accepted, tiers.<tier>.accepted,
counterparts.<id>.accepted, imports.accepted) that accepts nothing is fixed when it writes its path from the folder
holding the app (app/core/ports) where every such list writes it below the app (core/ports): when the path is
there once the app folder's name is taken off its start, the finding of the stale entry says to write it below the
app. The path so written is not accepted as well, so a path has one way to be written."""
from __future__ import annotations

from collections.abc import Callable


def stale_fix(written: str, app: str, there: Callable[[tuple[str, ...]], bool], fix: str) -> str:
    """The fix of a stale entry whose path is written: when it starts with the app folder's name (app) and what
    follows is there (by there, which takes its steps below the app), to write the path below the app; else fix."""
    if not written.startswith(f"{app}/"):
        return fix
    below = written[len(app) + 1:]
    steps = tuple(step for step in below.split("/") if step)
    if steps and there(steps):
        return f"write the path relative to the app: {below}, not {written}"
    return fix
