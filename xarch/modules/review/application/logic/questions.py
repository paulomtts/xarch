"""The question placement asks of a file, built from the profile's own words, the same for every profile: each part is
an option, described by its litmus test, or by its role when it has none; the same question of a piece of a file; and
what each question sends."""
from __future__ import annotations

from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.pieces import large, opening, sections, sent
from xarch.modules.review.domain.published import IMPORTS, Choice, Option, Request
from xarch.modules.review.domain.values import CodeFile, PartText

PLACEMENT = ("Which part of this architecture does this code belong in? Each option is a part and the test that "
             "decides whether code belongs in it.")
"""What placement asks, the wording the trials measured."""
OF_A_PIECE = "This text is one piece of a larger file."
"""What placement adds when it asks of a piece of a file, the wording the trials measured."""


def placement(parts: tuple[PartText, ...]) -> Choice:
    """The question placement asks: one option per part, in the profile's order, described by its litmus test, else
    by its role."""
    return Choice(PLACEMENT, tuple(Option(part.name, part.litmus or part.role) for part in parts))


def reordered(question: Choice) -> tuple[Choice, ...]:
    """The question in the other orders a file near its line is asked again in: its options rotated by a third and by
    two thirds of their number, each order once and never the first (one order for two options, none for one)."""
    count = len(question.options)
    shifts = dict.fromkeys(shift % count for shift in ((count + 1) // 3, (2 * count + 1) // 3) if count and shift % count)
    return tuple(Choice(question.ask, question.options[shift:] + question.options[:shift]) for shift in shifts)


def of_piece(question: Choice) -> Choice:
    """The question placement asks of a piece of a file: its own, saying the text is one piece of a larger file."""
    return Choice(f"{question.ask} {OF_A_PIECE}", question.options)


def piece_requests(file: CodeFile, root: str, mask: tuple[str, ...], context: str) -> tuple[tuple[Request, ...], int]:
    """What the question about each piece of a file judged sends, in order, the file's opening lines before each with
    context IMPORTS; and how many pieces are too small to be judged."""
    text = masked(file.text, file.imports, root, mask)
    found = sections(text, file.spans)
    judged = large(found)
    before = opening(text, file.spans) if context == IMPORTS else ""
    return (tuple(Request(file.file, file.part, len(sent(section, before)), sent(section, before), piece=section.name,
                          kind=section.kind, lines=section.lines) for section in judged), len(found) - len(judged))


def role_only(parts: tuple[PartText, ...]) -> tuple[str, ...]:
    """The parts that have no litmus test, which placement describes by their role alone."""
    return tuple(part.name for part in parts if not part.litmus)


def request(file: CodeFile, root: str, mask: tuple[str, ...] = (), also: tuple[str, ...] = ()) -> Request:
    """What the question about a file sends: its text masked, root being the app's import name (and also those of
    other apps it may be written for) and mask the texts the profile says review hides."""
    text = masked(file.text, file.imports, root, mask, also)
    return Request(file.file, file.part, len(text), text)


def characters(requests: tuple[Request, ...], question: Choice) -> int:
    """How many characters the requests send in all, each with the question."""
    asked = len(question.ask) + sum(len(o.name) + len(o.description) for o in question.options)
    return sum(len(r.text) + asked for r in requests)


def tokens(chars: int) -> int:
    """About how many tokens a number of characters sends: one for every four, rounded up."""
    return -(-chars // 4)
