"""What a file's answer says: the probability on the part it sits in, and whether that is below the part's line (the
profile's, else the default), so that the file reads as doubtful there; whether a file is near enough its line to be
asked again in other orders of the options, and the mean of its answers then; the order the readings are shown in,
the most doubtful first; how the files of each part read, so that a part low across the board points at its
litmus; and the pieces of a file ranked inside it."""
from __future__ import annotations

from xarch.modules.review.domain.published import (
    BAND,
    FEWEST_SUMMED,
    MARKED_SMALL,
    SHOWN,
    PartRead,
    PieceReading,
    PiecesRead,
    Reading,
    Request,
)
from xarch.modules.review.domain.values import Answer, CodeFile, PartText

FEWEST_NOTED = 3
"""The fewest files of a part that read as doubtful, more than a quarter of those read, for the run to say that the
part's litmus may not describe its files."""


def reading(request: Request, answer: Answer, part: PartText, orders: int = 1) -> Reading:
    """The reading of a file's answer, asked in orders orders of the options: the probability on its part (0 when the
    answer gives none), doubtful below the part's line, small under MARKED_SMALL characters."""
    probability = dict(answer.probabilities).get(request.part, 0.0)
    return Reading(request.file, request.part, request.chars, probability, part.line, probability < part.line,
                   answer.probabilities, answer.model, part.by_hand, orders, request.chars < MARKED_SMALL)


def asked_again(answer: Answer, part: PartText) -> bool:
    """Whether a file's first answer puts the probability on its part within BAND of the part's line, where the order
    of the options can move it across: the file is then asked again in other orders."""
    return round(abs(dict(answer.probabilities).get(part.name, 0.0) - part.line), 9) <= BAND


def averaged(answers: tuple[Answer, ...]) -> Answer:
    """One answer from the answers to the same question in several orders: each option's mean probability, in the
    order of the first; the first's model version; the tokens of all."""
    first = answers[0]
    each = [dict(answer.probabilities) for answer in answers]
    mean = tuple((name, sum(probabilities.get(name, 0.0) for probabilities in each) / len(each))
                 for name, _ in first.probabilities)
    return Answer(first.model, mean, sum(a.input_tokens for a in answers), sum(a.output_tokens for a in answers))


def ranked(readings: tuple[Reading, ...]) -> tuple[Reading, ...]:
    """The readings from the lowest probability on the file's own part to the highest, by file on a tie."""
    return tuple(sorted(readings, key=lambda found: (found.probability, found.file)))


def by_part(readings: tuple[Reading, ...], parts: tuple[PartText, ...]) -> tuple[PartRead, ...]:
    """How the files of each part with a file read this run read, in the profile's order of the parts."""
    found: list[PartRead] = []
    for part in parts:
        read = [item for item in readings if item.part == part.name]
        doubtful = sum(item.doubtful for item in read)
        if read:
            found.append(PartRead(part.name, len(read), doubtful, part.line, part.by_hand, len(read) >= FEWEST_SUMMED,
                                  doubtful >= FEWEST_NOTED and doubtful * 4 > len(read)))
    return tuple(found)


def ranks(requests: tuple[Request, ...]) -> bool:
    """Whether the pieces of a file judged can be ranked, and so are asked: at least two of them."""
    return len(requests) >= 2


def pieces_read(file: CodeFile, requests: tuple[Request, ...], answers: tuple[Answer | None, ...], too_small: int,
                context: str) -> PiecesRead:
    """The pieces of a file ranked by the probability on its part, the lowest SHOWN, ranked from 1 (by first line on
    a tie); none when fewer than two were judged (none was asked, and answers is empty), or when one of them has no
    answer."""
    if not ranks(requests):
        return PiecesRead(file.file, file.part, len(requests), too_small, context, ())
    answered = all(answer is not None for answer in answers)
    read = sorted(((dict(answer.probabilities).get(file.part, 0.0), item, answer)
                   for item, answer in zip(requests, answers, strict=True) if answer is not None),
                  key=lambda found: (found[0], found[1].lines))
    lowest = tuple(PieceReading(rank, item.kind, item.piece, item.lines, item.chars, probability, answer.probabilities)
                   for rank, (probability, item, answer) in enumerate(read[:SHOWN], 1))
    return PiecesRead(file.file, file.part, len(requests), too_small, context, lowest if answered else (), answered)
