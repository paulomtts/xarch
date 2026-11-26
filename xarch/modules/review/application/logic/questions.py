"""The question placement asks of a file, built from the profile's own words, the same for every profile: each part is
an option, described by its litmus test, or by its role when it has none; the same question of a piece of a file; and
what each question sends."""
from __future__ import annotations

from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.pieces import large, opening, sections, sent
from xarch.modules.review.domain.published import IMPORTS, YES_NO, Choice, Option, Request
from xarch.modules.review.domain.values import CodeFile, PartText
from xarch.profile_values.litmus import ALL, ANY

PLACEMENT = ("Which part of this architecture does this code belong in? Each option is a part and the test that "
             "decides whether code belongs in it.")
"""What placement asks, the wording the trials measured."""
OF_A_PIECE = "This text is one piece of a larger file."
OR, AND, IN_EVERY_CASE = " Or: ", " And: ", " And in every case: "
"""How placement's question joins the questions of a litmus list into one description of its part: the alternatives,
then the conditions."""
LITMUS = "litmus"
"""What the name of the question of an entry of a litmus list starts with, before its part and its label."""
YES, NO = "yes", "no"
"""The options of the question of an entry of a litmus list."""
FIRST = "placement"
"""The name placement's question travels under in a request, in its first order."""
"""What placement adds when it asks of a piece of a file, the wording the trials measured."""


def placement(parts: tuple[PartText, ...]) -> Choice:
    """The question placement asks: one option per part, in the profile's order, described by its litmus test, else
    by its role."""
    return Choice(PLACEMENT, tuple(Option(part.name, _described(part)) for part in parts))


def _described(part: PartText) -> str:
    """How placement's question describes a part: by its litmus of one text, or of a list of one entry, that entry's
    question; by a list of several, its `any` questions joined by OR, then its `all` questions after IN_EVERY_CASE,
    joined by AND; by its role when it has no litmus."""
    if not part.entries:
        return part.litmus or part.role
    if len(part.entries) == 1:
        return part.entries[0].ask
    alternatives = OR.join(entry.ask for entry in part.entries if entry.mode == ANY)
    conditions = AND.join(entry.ask for entry in part.entries if entry.mode == ALL)
    return f"{alternatives}{IN_EVERY_CASE}{conditions}" if alternatives and conditions else alternatives or conditions


def entry_questions(part: PartText) -> tuple[tuple[str, Choice], ...]:
    """The yes-or-no questions a file of the part is asked besides placement's, in the same request: one for each
    entry of its litmus list when it has two or more (none else), named `litmus.<part>.<label>`, asking the entry's
    question as written."""
    if len(part.entries) < 2:
        return ()
    return tuple((f"{LITMUS}.{part.name}.{entry.label}", Choice(entry.ask, (Option(YES, ""), Option(NO, "")), YES_NO))
                 for entry in part.entries)


def reordered(question: Choice) -> tuple[Choice, ...]:
    """The question in the other orders a file near its line is asked again in: its options rotated by a third and by
    two thirds of their number, each order once and never the first (one order for two options, none for one)."""
    count = len(question.options)
    shifts = dict.fromkeys(shift % count for shift in ((count + 1) // 3, (2 * count + 1) // 3) if count and shift % count)
    return tuple(Choice(question.ask, question.options[shift:] + question.options[:shift]) for shift in shifts)


def named_orders(others: tuple[Choice, ...]) -> tuple[tuple[str, Choice], ...]:
    """The other orders of placement's question, each under its name in a request: FIRST, `.order-`, and its number
    counted from 2, the first order being 1."""
    return tuple((f"{FIRST}.order-{number}", other) for number, other in enumerate(others, 2))


def carried(request: Request, questions: tuple[Choice, ...]) -> int:
    """How many characters a request that carries several questions sends: its text once, and each question."""
    return len(request.text) + sum(len(q.ask) + sum(len(o.name) + len(o.description) for o in q.options)
                                   for q in questions)


def of_piece(question: Choice) -> Choice:
    """The question placement asks of a piece of a file: its own, saying the text is one piece of a larger file."""
    return Choice(f"{question.ask} {OF_A_PIECE}", question.options)


def piece_requests(file: CodeFile, root: str, mask: tuple[str, ...], context: str) -> tuple[tuple[Request, ...], int]:
    """What the question about each piece of a file judged sends, in order, the file's opening lines before each with
    context IMPORTS; and how many pieces are too small to be judged."""
    text = masked(file.text, file.imports, root, mask, comments=file.comments)
    found = sections(text, file.spans)
    judged = large(found)
    before = opening(text, file.spans) if context == IMPORTS else ""
    return (tuple(Request(file.file, file.part, len(sent(section, before)), sent(section, before), piece=section.name,
                          kind=section.kind, lines=section.lines) for section in judged), len(found) - len(judged))


def role_only(parts: tuple[PartText, ...]) -> tuple[str, ...]:
    """The parts that have no litmus test, which placement describes by their role alone."""
    return tuple(part.name for part in parts if not part.litmus and not part.entries)


def request(file: CodeFile, root: str, mask: tuple[str, ...] = (), also: tuple[str, ...] = ()) -> Request:
    """What the question about a file sends: its text masked, its comments cut, root being the app's import name (and
    also those of other apps it may be written for) and mask the texts the profile says review hides."""
    text = masked(file.text, file.imports, root, mask, also, file.comments)
    return Request(file.file, file.part, len(text), text)


def characters(requests: tuple[Request, ...], question: Choice) -> int:
    """How many characters the requests send in all, each with the question."""
    asked = len(question.ask) + sum(len(o.name) + len(o.description) for o in question.options)
    return sum(len(r.text) + asked for r in requests)


def tokens(chars: int) -> int:
    """About how many tokens a number of characters sends: one for every four, rounded up."""
    return -(-chars // 4)
