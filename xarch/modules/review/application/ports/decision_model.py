from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.published import Choice, Sender
from xarch.modules.review.domain.values import Answer


class DecisionModel(Protocol):
    """A decision model, which answers a question of one answer out of several with the probability of each option."""

    def sends(self) -> Sender:
        """What a question is sent to: the service, where it answers, the model asked, the variable its key is read
        from, and whether the key is set now; raises Refused when the key set cannot be used, saying none of it."""
        ...

    def body(self, text: str, question: Choice) -> str:
        """The body the service would receive for the question about the text, as JSON text, the key left out."""
        ...

    def ask(self, text: str, question: Choice) -> Answer:
        """The answer to the question about the text; raises NoKey when the key is not set, Refused when it cannot be
        used, Unanswered when the service fails, its reason holding no key."""
        ...
