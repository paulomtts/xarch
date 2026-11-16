"""Where the answers to review's questions are kept, and under which key: a question about a text, asked of a model,
is answered once, and every later run that asks the same question of the same text reads the answer kept."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from xarch.modules.review.domain.published import CHOOSE, Choice
from xarch.modules.review.domain.values import Answer

CACHE = (".xarch", "cache", "review")
"""The folder the answers are kept in, below the project's root (the folder holding the app), which the project
commits."""
SUM_SLACK = 0.01
"""How far from 1 the probabilities of an answer kept may sum: what rounding leaves."""
RECORD = (".xarch", "calibration.json")
"""The file the evals of the profile's own held to their examples are recorded in, below the project's root, which the
project commits."""


def cache_folder(app: Path, given: Path | None) -> Path:
    """The folder given, else the project's own: CACHE below the folder holding app."""
    return given if given is not None else app.parent.joinpath(*CACHE)


def record_file(app: Path) -> Path:
    """The file the evals held to their examples are recorded in: RECORD below the folder holding app."""
    return app.parent.joinpath(*RECORD)


def request_key(model: str, text: str, question: Choice) -> str:
    """The key an answer is kept under: a hash of the model asked, the text sent and the question with its options in
    order, and its form unless it is a choice (so that a choice's key is what it was before questions had forms), so
    that a change to any of them asks again. It holds none of them."""
    asked = {"model": model, "text": text, "ask": question.ask,
             "options": [[option.name, option.description] for option in question.options]}
    form = {} if question.form == CHOOSE else {"form": question.form}
    canonical = json.dumps(asked | form, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fits(answer: Answer, question: Choice) -> bool:
    """Whether an answer kept answers the question: a probability for exactly its options, summing to 1 (within
    SUM_SLACK), and no count of tokens below 0. Any other is no answer to it, and the question is asked again."""
    names = [name for name, _ in answer.probabilities]
    if sorted(names) != sorted(option.name for option in question.options) or len(set(names)) != len(names):
        return False
    total = sum(found for _, found in answer.probabilities)
    return abs(total - 1) <= SUM_SLACK and answer.input_tokens >= 0 and answer.output_tokens >= 0


def versions(*answers: Answer) -> tuple[str, ...]:
    """The model versions that gave the answers, each once, sorted."""
    return tuple(sorted({answer.model for answer in answers}))
