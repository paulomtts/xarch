from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.ports.profile_output import ProfileOutput

SHOWN = 3
"""How many taken paths a refusal names before it counts the rest."""


class ProfileWriter:
    """Writes the files of a profile into a folder, and only new ones: it says which files already exist before it
    writes any, so that a refusal leaves nothing half written."""

    def __init__(self, output: ProfileOutput):
        self._output = output

    def taken(self, folder: Path, outputs: dict[str, bytes]) -> str:
        """The files of outputs that already exist in folder, as a phrase ending in the verb ("a, b and 2 more
        exist"), or "" when none does."""
        taken = [(folder / relative).as_posix() for relative in outputs if self._output.exists(folder / relative)]
        if not taken:
            return ""
        verb = "exists" if len(taken) == 1 else "exist"
        shown = ", ".join(taken[:SHOWN]) + (f" and {len(taken) - SHOWN} more" if len(taken) > SHOWN else "")
        return f"{shown} already {verb}"

    def write(self, folder: Path, outputs: dict[str, bytes]) -> None:
        for relative, data in outputs.items():
            self._output.write(folder / relative, data)
