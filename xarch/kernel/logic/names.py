"""Whether a text is a name a language allows, by the pattern its data file gives (a regular expression; any text but
nothing when it gives none), and whether a name is private, by how the language starts one ("" for none)."""
from __future__ import annotations

import re


def is_name(text: str, pattern: str) -> bool:
    """Whether text is a name the pattern allows; any text but nothing when the pattern is empty."""
    return re.fullmatch(pattern or ".+", text) is not None


def is_public_name(text: str, pattern: str, private: str) -> bool:
    """Whether text is a name the pattern allows that does not start as a private name does."""
    return is_name(text, pattern) and not (private and text.startswith(private))
