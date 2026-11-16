"""What a file's answer says: the probability on the part it sits in, and whether that is below the part's line (the
profile's, else the default), so that the file reads as doubtful there; and the order the readings are shown in, the most doubtful first."""
from __future__ import annotations

from xarch.modules.review.domain.published import Reading, Request
from xarch.modules.review.domain.values import Answer, PartText


def reading(request: Request, answer: Answer, part: PartText) -> Reading:
    """The reading of a file's answer: the probability on its part (0 when the answer gives none), doubtful below the
    part's line."""
    probability = dict(answer.probabilities).get(request.part, 0.0)
    return Reading(request.file, request.part, request.chars, probability, part.line, probability < part.line,
                   answer.probabilities, answer.model, part.by_hand)


def ranked(readings: tuple[Reading, ...]) -> tuple[Reading, ...]:
    """The readings from the lowest probability on the file's own part to the highest, by file on a tie."""
    return tuple(sorted(readings, key=lambda found: (found.probability, found.file)))
