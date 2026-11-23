from __future__ import annotations

from xarch.kernel.source import CommentSpan, Import
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import Unreadable


class SourceReadService:
    """Reads a source text of the app's language that is in no file, with the reader that reads the app's files, handed no
    standard module, no prefix of private names and no pattern of a special name: spec, which asks, has no profile."""

    def __init__(self, tree: SourceTree):
        self._tree = tree

    def imports(self, text: str) -> tuple[Import, ...]:
        """What the text imports, in order; raises Unreadable when it does not parse."""
        read = self._tree.parsed(text, frozenset(), private="", special="")
        if read.error is not None:
            raise Unreadable(read.error)
        return read.imports

    def comments(self, text: str) -> tuple[CommentSpan, ...]:
        """Where each comment of the text lies, in order; raises Unreadable when it does not parse."""
        read = self._tree.parsed(text, frozenset(), private="", special="")
        if read.error is not None:
            raise Unreadable(read.error)
        return tuple(comment.span for comment in read.comments)
