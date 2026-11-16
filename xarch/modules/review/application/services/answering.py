from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.answers import request_key
from xarch.modules.review.application.logic.sending import asks
from xarch.modules.review.application.ports.answers import Answers
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.domain.errors import Unanswered
from xarch.modules.review.domain.published import Choice
from xarch.modules.review.domain.values import Answer, Run


class AnsweringService:
    """Answers the questions of a run about texts: the answer kept in the run's folder is read, else the decision model
    is asked and its answer kept; once it fails, nothing more is asked. Each answer comes back with the run as it now
    stands."""

    def __init__(self, model: DecisionModel, answers: Answers):
        self._model, self._answers = model, answers

    def kept(self, run: Run, text: str, question: Choice) -> Answer | None:
        """The answer kept for the question about the text; None when there is none."""
        return self._answers.get(run.folder, request_key(self._model.sends().model, text, question))

    def answer(self, run: Run, text: str, question: Choice) -> tuple[Answer | None, Run]:
        """The answer kept, else the decision model's, which is kept; None when there is none (offline, or the decision
        model failed now or before)."""
        kept = self.kept(run, text, question)
        if not asks(kept, run.offline, bool(run.failure)):
            return kept, run if kept is None else replace(run, reused=(*run.reused, kept))
        try:
            answer = self._model.ask(text, question)
        except Unanswered as e:
            return None, replace(run, failure=e.reason)
        self._answers.put(run.folder, request_key(self._model.sends().model, text, question), answer)
        return answer, replace(run, asked=(*run.asked, answer))

    def all(self, run: Run, text: str, questions: tuple[Choice, ...]) -> tuple[tuple[Answer, ...] | None, Run]:
        """The answer to each question about the text, in order; None when one has none."""
        found: list[Answer | None] = []
        for question in questions:
            answer, run = self.answer(run, text, question)
            found.append(answer)
        return (None if any(answer is None for answer in found) else tuple(a for a in found if a is not None)), run
