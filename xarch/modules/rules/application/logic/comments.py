"""The no-comments guard: a `#` comment, whole-line or trailing, is a violation; a docstring is not a comment.

Allowed are the directives tools read: `# type: ignore...`, `# noqa...` and `# pragma: ...`, a shebang on line 1 and
an encoding declaration (PEP 263) on line 1 or 2.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Comment, SourceFile

_DIRECTIVE = re.compile(r"#\s*(type:\s*ignore|noqa|pragma:)")
_ENCODING = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*[-\w.]+")
MESSAGE = "a comment: say it in a docstring or a name (no-comments)"


def allowed(comment: Comment) -> bool:
    if _DIRECTIVE.match(comment.text):
        return True
    if comment.line == 1 and comment.text.startswith("#!"):
        return True
    return comment.line <= 2 and bool(_ENCODING.match(comment.text))


def violations(files: Iterable[SourceFile]) -> list[Violation]:
    return [Violation(f.name, c.line, MESSAGE) for f in files for c in f.comments if not allowed(c)]
