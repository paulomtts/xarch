from __future__ import annotations

from typing import Protocol

from xarch.kernel.source import CommentSpan, Import, Unparsable


class ExampleReader(Protocol):
    """What the source of an example says, read by the reader of the app's language."""

    def imports(self, text: str) -> tuple[Import, ...] | Unparsable:
        """The imports of an example's text, in order, or where and why it does not parse."""
        ...

    def comments(self, text: str) -> tuple[CommentSpan, ...] | Unparsable:
        """Where each comment of an example's text lies, in order, or where and why it does not parse."""
        ...
