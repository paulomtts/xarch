"""Findings at a place in a file tree. No business meaning: what was found is in the message, what to do in the fix. A
violation fails the check; a weak finding is listed beside the violations and fails only a strict check; At is the
place alone."""
from __future__ import annotations

import re
from dataclasses import dataclass

RULES = ("rules", "libraries", "forbidden", "tiers", "types-only", "cycles", "package-only", "scenario-coverage",
         "no-comments", "stand-ins", "closed-tree", "must-import", "no-duplicates", "no-twins", "dead-code",
         "pass-through", "holds", "no-callbacks", "names", "built-by", "private-imports", "structure", "test-tree",
         "syntax")
"""The stable ids of the checks xarch has, as a violation names them."""
OWN_ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
"""How the id of a check the profile writes itself is written: lowercase words joined by `-`."""


@dataclass(frozen=True)
class Violation:
    """file and line (0: the file as a whole) say where; message what was found, as a sentence; rule is the stable id
    of the check that found it (one of RULES, or, for a check the profile writes itself, own, its id: lowercase words
    joined by `-`, none of RULES); fix is what to do about it, one imperative sentence specific to the finding. A
    violation with a blank fix, or of a rule that is neither, cannot be made."""
    file: str
    line: int
    message: str
    rule: str
    fix: str
    own: bool = False

    def __post_init__(self) -> None:
        if self.own and (self.rule in RULES or not OWN_ID.fullmatch(self.rule)):
            raise ValueError(f"a violation of a check of the profile's own names {self.rule!r}: its id is lowercase words "
                             f"joined by `-`, and none of {', '.join(sorted(RULES))}")
        if not self.own and self.rule not in RULES:
            raise ValueError(f"a violation names an unknown rule {self.rule!r}: use one of {', '.join(sorted(RULES))}")
        if not self.fix.strip():
            where = f"{self.file}:{self.line}" if self.line else self.file
            raise ValueError(f"a violation of rule {self.rule!r} at {where} has no fix: say what to do about it")

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{where}: {self.message}"


@dataclass(frozen=True)
class At:
    """A place in a file: how the file is shown and the line."""
    file: str
    line: int


@dataclass(frozen=True)
class Weak:
    """A check satisfied to the letter only, which is not a violation: the stable id of the check it concerns (one of
    RULES), where, and why; fix is what to do about it, empty when there is no advice."""
    rule: str
    file: str
    line: int
    message: str
    fix: str = ""
