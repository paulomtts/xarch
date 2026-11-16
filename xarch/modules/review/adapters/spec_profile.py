"""What review reads of a profile, read by the spec module: the only file in review that names spec, and it names only
spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import Choice, Option
from xarch.modules.review.domain.values import EvalText, PartText, Words
from xarch.modules.spec.contract import LINE, Eval, ProfileRefused, ProfileResult, ProfileView
from xarch.profile_values.checks import Condition


class _Spec(Protocol):
    """The little review uses of spec's controller."""

    def profile(self, location: str) -> ProfileResult: ...


class SpecWords:
    """Satisfies review's Profile port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def words(self, profile: str) -> Words:
        """Each part's line is the one the profile writes, else spec's default. A profile spec refuses raises Refused
        with spec's reason."""
        match self._spec.profile(profile):
            case ProfileView(parts=parts, never=never, mask=mask, lines=lines, evals=evals):
                return Words(tuple(PartText(part.name, part.shown, part.litmus, part.role, lines.get(part.name, LINE),
                                            part.name in lines) for part in parts), never, mask,
                             tuple(_eval(name, asked) for name, asked in evals.items()))
            case ProfileRefused(reason):
                raise Refused(reason)


def _eval(name: str, asked: Eval) -> EvalText:
    question = Choice(asked.ask, tuple(Option(option, said) for option, said in asked.options), asked.form)
    return EvalText(name, question, asked.flagged, asked.line, asked.message, asked.fix, asked.flagged_examples,
                    asked.clean_examples, _reads(asked))


def _reads(asked: Eval) -> str:
    """What the eval reads, where and passing which filters, as one text that changes when any of them does."""
    def written(conditions: tuple[Condition, ...]) -> tuple[str, ...]:
        return tuple(f"{'not ' if c.negated else ''}{c.name} {c.value}".strip() for c in conditions)

    return " | ".join((asked.reads, asked.within.part, "where", *written(asked.within.where), "keep",
                       *written(asked.keep)))
