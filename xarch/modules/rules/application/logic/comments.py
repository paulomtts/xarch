"""The no-comments guard: a line comment, whole-line or trailing, is a violation; a docstring is not a comment.

Allowed are the comments the language's tools read, as its data file names them: the directives after its comment
marker (a space in one standing for any spaces), a shebang on line 1, and an encoding declaration on line 1 or 2.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Comment, SourceFile

MESSAGE = "a comment (no-comments)"
FIX = "say it in a docstring or a name, and delete the comment"


def allowed(comment: Comment, language: LanguageView) -> bool:
    marker = re.escape(language.comment)
    words = "|".join(r"\s*".join(re.escape(part) for part in word.split(" ")) for word in language.directives)
    if words and re.match(rf"{marker}\s*({words})", comment.text):
        return True
    if comment.line == 1 and language.shebang and comment.text.startswith(language.shebang):
        return True
    return comment.line <= 2 and bool(language.encoding) and bool(
        re.match(rf"^[ \t\f]*{marker}.*?{language.encoding}", comment.text))


def violations(files: Iterable[SourceFile], language: LanguageView) -> list[Violation]:
    return [Violation(f.name, c.line, MESSAGE, "no-comments", FIX) for f in files for c in f.comments
            if not allowed(c, language)]
