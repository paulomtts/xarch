"""What the profile's rules leave of a file's answer: a part whose `holds` the file would break were it to lie there
cannot be where it belongs, whatever the file is about, and is ruled out (HOLDS): its probability is dropped, and what
remains is made to sum to 1 again; a part the answer puts nothing on is left as it is, there being nothing to drop.
The file's own part is never ruled out (`check` says when the file breaks it), and an
answer that would leave nothing (its own part at 0 and every other part ruled out) is read as it was answered, nothing
ruled out."""
from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.domain.published import HOLDS, RuledOut
from xarch.modules.review.domain.values import Answer


def ruled(answer: Answer, part: str, breaks: tuple[str, ...]) -> tuple[Answer, tuple[RuledOut, ...]]:
    """The answer of a file of part with what remains once each part of breaks but its own that the answer puts
    anything on is ruled out, summing to 1, in the order answered; and the parts ruled out, each with the probability
    the answer put on it, in that order."""
    out = tuple(RuledOut(name, HOLDS, probability) for name, probability in answer.probabilities
                if name in breaks and name != part and probability > 0)
    dropped = {item.part for item in out}
    kept = tuple((name, probability) for name, probability in answer.probabilities if name not in dropped)
    total = sum(probability for _, probability in kept)
    if not out or total <= 0:
        return answer, ()
    return replace(answer, probabilities=tuple((name, probability / total) for name, probability in kept)), out
