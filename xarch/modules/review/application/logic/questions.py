"""The question placement asks of a file, built from the profile's own words, the same for every profile: each part is
an option, described by its litmus test, or by its role when it has none."""
from __future__ import annotations

from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.domain.published import Choice, Option, Request
from xarch.modules.review.domain.values import CodeFile, PartText

PLACEMENT = ("Which part of this architecture does this code belong in? Each option is a part and the test that "
             "decides whether code belongs in it.")
"""What placement asks, the wording the trials measured."""


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


def role_only(parts: tuple[PartText, ...]) -> tuple[str, ...]:
    """The parts that have no litmus test, which placement describes by their role alone."""
    return tuple(part.name for part in parts if not part.litmus)


def request(file: CodeFile, root: str, mask: tuple[str, ...] = ()) -> Request:
    """What the question about a file sends: its text masked, root being the app's import name and mask the texts the
    profile says review hides."""
    return Request(file.file, file.part, len(file.text), masked(file.text, file.imports, root, mask))


def characters(requests: tuple[Request, ...], question: Choice) -> int:
    """How many characters the requests send in all, each with the question."""
    asked = len(question.ask) + sum(len(o.name) + len(o.description) for o in question.options)
    return sum(len(r.text) + asked for r in requests)


def tokens(chars: int) -> int:
    """About how many tokens a number of characters sends: one for every four, rounded up."""
    return -(-chars // 4)
