"""A litmus test as a profile writes it under `parts.<part>.litmus` or `tiers.<tier>.litmus`: one text, or a list of
entries, each a question with its label and its mode."""
from __future__ import annotations

from dataclasses import dataclass

ANY, ALL = "any", "all"
"""The modes of an entry of a litmus written as a list: an alternative, and a condition. Code belongs when at least one
`any` entry answers yes (when there is any `any` entry) and every `all` entry answers yes."""


@dataclass(frozen=True)
class Litmus:
    """One entry of a litmus written as a list: the question it asks; its label, as written, else its position in the
    list counted from 1; and its mode, ANY or ALL."""
    ask: str
    label: str
    mode: str = ANY

