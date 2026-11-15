"""The syntax rule: a file that does not parse is a violation, and no other check reads it."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import SourceFile

SYNTAX = "syntax"
"""The rule of a file that does not parse."""


def violations(files: Iterable[SourceFile]) -> list[Violation]:
    """Every file that does not parse, at the line its error is on."""
    return [Violation(f.name, f.error[0], f.error[1], SYNTAX, "correct the syntax so that the file can be read")
            for f in files if f.error is not None]
