"""The values review reads through its ports: the profile's words review reads (its parts as placement offers them,
and what review may send), and the files found at the paths given, read or not, with their pieces; and the pieces as
review judges them."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.source import Import, Unparsable
from xarch.modules.review.domain.published import LeftOut


@dataclass(frozen=True)
class PartText:
    """A part as placement offers it: its name, its folder as the docs show it, its litmus test ("" for none), its
    role, the line below which a file reads as doubtful there, and whether the profile sets that line by hand."""
    name: str
    folder: str
    litmus: str
    role: str
    line: float
    by_hand: bool = False


@dataclass(frozen=True)
class Words:
    """What review reads of a profile: its parts, in its order; the paths below the app of the files review never
    sends; and the texts it hides before it sends, each as the profile writes it."""
    parts: tuple[PartText, ...]
    never: tuple[str, ...] = ()
    mask: tuple[str, ...] = ()


@dataclass(frozen=True)
class Span:
    """A piece of a file as its language's reader cuts it: its kind, as the reader names it (a function, a class, a
    method); its name; the class it is a method of ("" for a piece at the top level); and the first and last lines it
    spans, counted from 1."""
    kind: str
    name: str
    owner: str
    lines: tuple[int, int]


@dataclass(frozen=True)
class CodeFile:
    """A source file of the app in a part, read: the file, as `check` shows it; the part; its text; its imports; how
    it fails to parse (None: it parses); and its pieces, in the order of their first line."""
    file: str
    part: str
    text: str
    imports: tuple[Import, ...] = ()
    error: Unparsable | None = None
    spans: tuple[Span, ...] = ()


@dataclass(frozen=True)
class Section:
    """A piece of a file as review judges it: its name as shown (Class.method for a method; the names joined, for
    small pieces merged); its kind, the first piece's; the first and last lines it spans; its text, masked; and, for a
    method, the text of its class before its first method, sent with it ("" for any other)."""
    name: str
    kind: str
    lines: tuple[int, int]
    text: str
    head: str = ""


@dataclass(frozen=True)
class Found:
    """The files found at the paths given, each once: those read, in a part of the app, and those that are not, each
    with why, both in the order they were found."""
    read: tuple[CodeFile, ...]
    unread: tuple[LeftOut, ...] = ()


@dataclass(frozen=True)
class Answer:
    """What the decision model answered to a question of one answer out of several: the model version that answered,
    the probability of each option by its name, in the order of the question, and the tokens the question and the
    answer cost."""
    model: str
    probabilities: tuple[tuple[str, float], ...]
    input_tokens: int = 0
    output_tokens: int = 0
