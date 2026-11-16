"""How review cuts a text into lines: as the language's reader numbers them, at a line feed, a carriage return and
line feed, or a carriage return alone, and nowhere else (a form feed, a vertical tab or a Unicode line separator
inside a line is part of it), so that the line an import or a piece is said to start on is the line cut."""
from __future__ import annotations

import re

BREAK = re.compile(r"(?<=\r\n)|(?<=\r)(?!\n)|(?<=\n)")
"""Where a line ends: after a line feed, a carriage return and line feed, or a carriage return not followed by one."""


def lines(text: str) -> tuple[str, ...]:
    """The lines of the text, each with its line break, counted from the first; no empty line after the last break."""
    return tuple(line for line in BREAK.split(text) if line)
