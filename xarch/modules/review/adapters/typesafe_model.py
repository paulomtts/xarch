"""Review's decision model over TypeSafe's client in `platform/`: the only file in review that names a service. It says,
as data, the service it sends to, where it answers, the model asked and the variable its key is read from, so that
review's output can name them while review's own code names none."""
from __future__ import annotations

from collections.abc import Callable

from xarch.modules.review.domain.errors import NoKey, Unanswered
from xarch.modules.review.domain.published import Choice, Option, Sender
from xarch.modules.review.domain.values import Answer
from xarch.platform.data_files import DataFileWriter
from xarch.platform.typesafe import ChoiceAnswer, ChoiceQuestion, Response, TypeSafe, TypeSafeError, Usage, build_request

SERVICE = "TypeSafe"
"""What review sends to, by name: the provider of the decision model."""
KEY = "TYPESAFE_API_KEY"
"""The variable of the environment the key is read from: set, it alone allows review to send."""
NAME = "placement"
"""The name the question travels under in a request."""


class TypeSafeModel:
    """Satisfies review's DecisionModel by translating its question into TypeSafe's and the answer back. connect gives
    the client with the key set, or None when it is not; the key never passes through here."""

    def __init__(self, connect: Callable[[], TypeSafe | None], model: str, at: str, writer: DataFileWriter):
        self._connect, self._model, self._at, self._writer = connect, model, at, writer

    def sends(self) -> Sender:
        return Sender(SERVICE, self._at, self._model, KEY, self._connect() is not None)

    def body(self, text: str, question: Choice) -> str:
        return self._writer.json(build_request(self._model, text, {NAME: _question(question)}))

    def ask(self, text: str, question: Choice) -> Answer:
        """A failure of the client raises Unanswered with the client's message, which holds no key."""
        client = self._connect()
        if client is None:
            raise NoKey(KEY)
        try:
            response = client.ask(text, {NAME: _question(question)})
        except TypeSafeError as e:
            raise Unanswered(str(e)) from None
        return _answer(response, question.options)


def _question(question: Choice) -> ChoiceQuestion:
    return ChoiceQuestion({option.name: option.description for option in question.options}, question.ask)


def _answer(response: Response, options: tuple[Option, ...]) -> Answer:
    return Answer(response.model, _distribution(response.answers[NAME], options), *_tokens(response.usage))


def _distribution(answer: ChoiceAnswer, options: tuple[Option, ...]) -> tuple[tuple[str, float], ...]:
    return tuple((option.name, float(answer.probabilities.get(option.name, 0.0))) for option in options)


def _tokens(usage: Usage) -> tuple[int, int]:
    return usage.input_tokens, usage.output_tokens
