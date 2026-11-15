from __future__ import annotations

from xarch.kernel.logic.source import Import
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.domain.errors import Unreadable


class SourceReadService:
    """Reads a source text of the app's language that is in no file, with the reader that reads the app's files."""

    def __init__(self, tree: SourceTree):
        self._tree = tree

    def imports(self, text: str) -> tuple[Import, ...]:
        """What the text imports, in order; raises Unreadable when it does not parse."""
        read = self._tree.parsed(text)
        if read.error is not None:
            raise Unreadable(read.error)
        return read.imports
