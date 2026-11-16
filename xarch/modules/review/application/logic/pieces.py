"""How review cuts a file into the pieces it ranks, by the spans its language's reader gives: each function and class
at the top level; a class over SPLIT_CHARS characters as its methods instead, each sent with the class's text before its
first method; a piece under MERGE_CHARS characters joined to the next piece of the same class (or of the top level),
the last one to the one before; and of those, the ones of PIECE_CHARS characters or more judged. What is sent for a
piece is its text, after the file's opening lines (those before its first piece) when context is asked for."""
from __future__ import annotations

from xarch.modules.review.application.logic.lines import lines as cut
from xarch.modules.review.domain.published import MERGE_CHARS, PIECE_CHARS, SPLIT_CHARS
from xarch.modules.review.domain.values import Section, Span


def _text(lines: list[str], span: tuple[int, int]) -> str:
    return "".join(lines[span[0] - 1:span[1]])


def _whole(span: Span, spans: tuple[Span, ...], lines: list[str]) -> tuple[Section, ...]:
    """A piece at the top level as one section; a class over SPLIT_CHARS characters with methods as its methods."""
    text = _text(lines, span.lines)
    methods = [s for s in spans if s.owner == span.name and span.lines[0] <= s.lines[0] <= span.lines[1]]
    if len(text) <= SPLIT_CHARS or not methods:
        return (Section(span.name, span.kind, span.lines, text),)
    head = _text(lines, (span.lines[0], methods[0].lines[0] - 1))
    return tuple(Section(f"{span.name}.{s.name}", s.kind, s.lines, _text(lines, s.lines), head) for s in methods)


def _joined(first: Section, then: Section, lines: list[str]) -> Section:
    span = (first.lines[0], then.lines[1])
    return Section(f"{first.name}, {then.name}", first.kind, span, _text(lines, span), first.head)


def _merged(found: list[Section], lines: list[str]) -> tuple[Section, ...]:
    """Each section under MERGE_CHARS joined to the next of the same class, the last of a class to the one before."""
    done: list[Section] = []
    small: Section | None = None
    for section in found:
        if small is not None and small.head == section.head:
            section = _joined(small, section, lines)
        elif small is not None:
            done = _closed(done, small, lines)
        small = section if len(section.text) < MERGE_CHARS else None
        if small is None:
            done.append(section)
    return tuple(_closed(done, small, lines) if small is not None else done)


def _closed(done: list[Section], small: Section, lines: list[str]) -> list[Section]:
    """The small section left over at the end of its class, joined to the one before it when that is of its class."""
    if done and done[-1].head == small.head:
        return done[:-1] + [_joined(done[-1], small, lines)]
    return done + [small]


def sections(text: str, spans: tuple[Span, ...]) -> tuple[Section, ...]:
    """The pieces of the text (the file's, masked) review ranks, in order, before any is left out for its size."""
    lines = list(cut(text))
    found = [section for span in spans if not span.owner for section in _whole(span, spans, lines)]
    return _merged(found, lines)


def large(found: tuple[Section, ...]) -> tuple[Section, ...]:
    """The sections of PIECE_CHARS characters or more: the only ones judged."""
    return tuple(section for section in found if len(section.text) >= PIECE_CHARS)


def opening(text: str, spans: tuple[Span, ...]) -> str:
    """The lines of the text before its first piece: what `--context imports` sends before each piece."""
    first = min((span.lines[0] for span in spans), default=1)
    return "".join(cut(text)[:first - 1])


def sent(section: Section, context: str) -> str:
    """What is sent for a section: the context, then its class's text before its first method, then its own text."""
    return context + section.head + section.text
