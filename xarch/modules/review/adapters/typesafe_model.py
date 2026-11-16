"""Review's decision model over TypeSafe's client in `platform/`: the only file in review that names a service. It says,
as data, the service it sends to, where it answers, the model asked and the variable its key is read from, so that
review's output can name them while review's own code names none."""
from __future__ import annotations

from collections.abc import Callable

from xarch.modules.review.domain.errors import NoKey, Refused, Unanswered
from xarch.modules.review.domain.published import SCORE, YES_NO, Choice, Option, Sender
from xarch.modules.review.domain.values import Answer
from xarch.platform.data_files import DataFileWriter
from xarch.platform.typesafe import (
    ChoiceAnswer,
    ChoiceQuestion,
    NoulAnswer,
    NoulQuestion,
    Question,
    Response,
    ScoreAnswer,
    ScoreQuestion,
    TypeSafe,
    TypeSafeError,
    Usage,
    build_request,
)

SERVICE = "TypeSafe"
"""What review sends to, by name: the provider of the decision model."""
KEY = "TYPESAFE_API_KEY"
"""The variable of the environment the key is read from: set, it alone allows review to send."""
NAME = "placement"
"""The name the question travels under in a request."""
YES, NO = "yes", "no"
"""The options of a yes or no, by name, as review's question names them."""


class TypeSafeModel:
    """Satisfies review's DecisionModel by translating its question into TypeSafe's and the answer back. connect gives
    the client with the key set, or None when it is not; the key never passes through here, and a key the client
    refuses raises Refused with a sentence that holds none of it."""

    def __init__(self, connect: Callable[[], TypeSafe | None], model: str, at: str, writer: DataFileWriter):
        self._connect, self._model, self._at, self._writer = connect, model, at, writer

    def sends(self) -> Sender:
        return Sender(SERVICE, self._at, self._model, KEY, self._client() is not None)

    def body(self, text: str, question: Choice) -> str:
        return self._writer.json(build_request(self._model, text, {NAME: _question(question)}))

    def ask(self, text: str, question: Choice) -> Answer:
        """A failure of the client raises Unanswered with the client's message, which holds no key."""
        client = self._client()
        if client is None:
            raise NoKey(KEY)
        try:
            response = client.ask(text, {NAME: _question(question)})
        except TypeSafeError as e:
            raise Unanswered(str(e)) from None
        return _answer(response, question.options)


    def _client(self) -> TypeSafe | None:
        try:
            return self._connect()
        except TypeSafeError:
            raise Refused(f"{KEY} cannot be used: it holds a character a request header cannot carry; set it to the "
                          "key alone") from None


def _question(question: Choice) -> Question:
    """A yes or no as TypeSafe's noul, its yes and no as true and false (when described); a score as its levels in
    order; any other as a choice of its options."""
    said = {option.name: option.description or None for option in question.options}
    if question.form == YES_NO:
        return NoulQuestion(question.ask, said.get(YES), said.get(NO))
    if question.form == SCORE:
        return ScoreQuestion([option.description for option in question.options], question.ask)
    return ChoiceQuestion({option.name: option.description for option in question.options}, question.ask)


def _answer(response: Response, options: tuple[Option, ...]) -> Answer:
    return Answer(response.model, _distribution(response.answers[NAME], options), *_tokens(response.usage))


def _distribution(answer: NoulAnswer | ChoiceAnswer | ScoreAnswer,
                  options: tuple[Option, ...]) -> tuple[tuple[str, float], ...]:
    """The probability of each option of the question, in its order: of yes and of no for a noul; of each level, by
    its number from 0, for a score."""
    if isinstance(answer, NoulAnswer):
        return (YES, float(answer.noul)), (NO, 1.0 - float(answer.noul))
    return tuple((option.name, float(answer.probabilities.get(option.name, 0.0))) for option in options)


def _tokens(usage: Usage) -> tuple[int, int]:
    return usage.input_tokens, usage.output_tokens
