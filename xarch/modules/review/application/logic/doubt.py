"""What a file's answer says: the probability on the part it sits in, and whether that is below the part's line (the
profile's, else the default), so that the file reads as doubtful there; whether a file is near enough its line to be
asked again in other orders of the options, and the mean of its answers then; and the order the readings are shown
in, the most doubtful first."""
from __future__ import annotations

from xarch.modules.review.domain.published import BAND, Reading, Request
from xarch.modules.review.domain.values import Answer, PartText


def reading(request: Request, answer: Answer, part: PartText, orders: int = 1) -> Reading:
    """The reading of a file's answer, asked in orders orders of the options: the probability on its part (0 when the
    answer gives none), doubtful below the part's line."""
    probability = dict(answer.probabilities).get(request.part, 0.0)
    return Reading(request.file, request.part, request.chars, probability, part.line, probability < part.line,
                   answer.probabilities, answer.model, part.by_hand, orders)


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
