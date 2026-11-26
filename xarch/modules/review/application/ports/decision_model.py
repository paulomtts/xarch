from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.published import Choice, Sender
from xarch.modules.review.domain.values import Answer


class DecisionModel(Protocol):
    """A decision model, which answers a question of one answer out of several with the probability of each option."""

    def sends(self) -> Sender:
        """What a question is sent to: the service, where it answers, the model asked, the variable its key is read
        from, whether the key is set now, and why the key set cannot be used, saying none of it."""
        ...

    def body(self, text: str, question: Choice) -> str:
        """The body the service would receive for the question about the text, as JSON text, the key left out."""
        ...

    def ask(self, text: str, question: Choice) -> Answer:
        """The answer to the question about the text; raises NoKey when the key is not set, Refused when it cannot be
        used, NotAccepted when the service refuses this request alone as its own fault, Unanswered when it fails
        otherwise, its reason holding no key."""
        ...

    def body_all(self, text: str, questions: tuple[tuple[str, Choice], ...]) -> str:
        """The body the service would receive for the questions about the text, each under its name, in one request,
        the text sent once, as JSON text, the key left out."""
        ...

    def ask_all(self, text: str, questions: tuple[tuple[str, Choice], ...]) -> tuple[Answer, ...]:
        """The answer to each question about the text, each under its name, in order, asked in one request that sends
        the text once: the tokens the request cost on the first answer, none on the others; raises as ask does, for
        the request whole."""
        ...
