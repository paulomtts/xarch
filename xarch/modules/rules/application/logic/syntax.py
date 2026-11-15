"""The syntax rule: a file that does not parse is a violation, and no other check reads it. The violation says what the
parser said, as a file that is not valid in the language of the app."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Profile, SourceFile

SYNTAX = "syntax"
"""The rule of a file that does not parse."""


def violations(files: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    """Every file that does not parse, at the line its error is on."""
    title = profile.language.title or "source"
    return [Violation(f.name, f.error.line, f"not valid {title}: {f.error.message}", SYNTAX,
                      "correct the syntax so that the file can be read")
            for f in files if f.error is not None]
