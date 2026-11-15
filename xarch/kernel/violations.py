"""A finding at a place in a file tree. No business meaning: what was found is in the message, what to do in the fix."""
from __future__ import annotations

from dataclasses import dataclass

RULES = ("rules", "libraries", "forbidden", "tiers", "types-only", "cycles", "package-only", "scenario-coverage",
         "no-comments", "stand-ins", "closed-tree", "must-import", "no-duplicates", "no-twins", "dead-code",
         "pass-through", "holds", "no-callbacks", "names", "built-by", "private-imports", "structure", "test-tree",
         "syntax")
"""The stable ids of the checks, as a violation names them: the only values its rule may take."""


@dataclass(frozen=True)
class Violation:
    """file and line (0: the file as a whole) say where; message what was found, as a sentence; rule is the stable id
    of the check that found it (one of RULES); fix is what to do about it, one imperative sentence specific to the
    finding. A violation with a blank fix, or of a rule not in RULES, cannot be made."""
    file: str
    line: int
    message: str
    rule: str
    fix: str

    def __post_init__(self) -> None:
        if self.rule not in RULES:
            raise ValueError(f"a violation names an unknown rule {self.rule!r}: use one of {', '.join(sorted(RULES))}")
        if not self.fix.strip():
            where = f"{self.file}:{self.line}" if self.line else self.file
            raise ValueError(f"a violation of rule {self.rule!r} at {where} has no fix: say what to do about it")

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{where}: {self.message}"
