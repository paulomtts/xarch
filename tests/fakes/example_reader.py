"""In-memory implementation of spec's ExampleReader port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.kernel.source import CommentSpan, Import, Unparsable


class FakeExampleReader:
    """Satisfies spec's ExampleReader: what each text given imports, or where it does not parse, and where the comments
    of each text given lie; any other text imports nothing and holds no comment."""

    def __init__(self, reads: dict[str, tuple[Import, ...] | Unparsable] | None = None,
                 comments: dict[str, tuple[CommentSpan, ...] | Unparsable] | None = None):
        self._reads = dict(reads or {})
        self._comments = dict(comments or {})

    def imports(self, text: str) -> tuple[Import, ...] | Unparsable:
        return self._reads.get(text, ())

    def comments(self, text: str) -> tuple[CommentSpan, ...] | Unparsable:
        return self._comments.get(text, ())
