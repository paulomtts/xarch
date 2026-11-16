"""Review's decision model over TypeSafe's client: what it says it sends to, the question translated into TypeSafe's
and the answer back in review's words, a failure of the client as Unanswered with the client's message, and no client
(no key set) as NoKey. The client here is a stand-in that answers without the network."""
import json

import pytest

from xarch.modules.review.adapters.typesafe_model import KEY, NAME, SERVICE, TypeSafeModel
from xarch.modules.review.domain.errors import NoKey, Unanswered
from xarch.modules.review.domain.published import SCORE, YES_NO, Choice, Option, Sender
from xarch.modules.review.domain.values import Answer
from xarch.platform.data_files import DataFileWriter
from xarch.platform.typesafe import (
    ChoiceAnswer,
    ChoiceQuestion,
    InvalidRequestError,
    NoulAnswer,
    NoulQuestion,
    Response,
    ScoreAnswer,
    ScoreQuestion,
    Usage,
)

QUESTION = Choice("Which part?", (Option("domain", "Is it a value?"), Option("main", "starts the app")))
AT = "https://model.example.test"


class Client:
    """TypeSafe's client as the adapter uses it: it answers each question with response, or raises error, and records
    what it was asked."""

    def __init__(self, response: Response | None = None, error: Exception | None = None):
        self.response, self.error, self.asked = response, error, []

    def ask(self, state, questions):
        self.asked.append((state, dict(questions)))
        if self.error is not None:
            raise self.error
        return self.response


def model(client: Client | None) -> TypeSafeModel:
    return TypeSafeModel(lambda: client, "jev-1.14.0", AT, DataFileWriter())


@pytest.mark.parametrize("client, keyed", [
    pytest.param(Client(), True, id="with a client the key is set"),
    pytest.param(None, False, id="with none it is not"),
])
def test_it_says_the_service_where_it_answers_the_model_and_the_variable_of_the_key(client, keyed):
    assert model(client).sends() == Sender(SERVICE, AT, "jev-1.14.0", KEY, keyed)
    assert (SERVICE, KEY) == ("TypeSafe", "TYPESAFE_API_KEY")


def test_the_question_is_sent_as_one_choice_of_the_parts_with_their_descriptions_and_the_text_as_the_state():
    answer = ChoiceAnswer("main", 0.8, {"main": 0.9, "domain": 0.1})
    client = Client(Response("jev-1.14.0", {NAME: answer}, Usage(2400, 3)))
    assert model(client).ask("class A: ...\n", QUESTION) == Answer("jev-1.14.0", (("domain", 0.1), ("main", 0.9)),
                                                                   2400, 3)
    assert client.asked == [("class A: ...\n", {NAME: ChoiceQuestion({"domain": "Is it a value?",
                                                                      "main": "starts the app"}, "Which part?")})]


def test_an_option_the_answer_gives_nothing_holds_0():
    client = Client(Response("jev-1.14.0", {NAME: ChoiceAnswer("main", 1, {"main": 1})}, Usage(1, 1)))
    assert model(client).ask("x", QUESTION).probabilities == (("domain", 0.0), ("main", 1.0))


def test_a_failure_of_the_client_is_unanswered_with_its_message():
    with pytest.raises(Unanswered, match="TypeSafe answered 413: too big"):
        model(Client(error=InvalidRequestError("TypeSafe answered 413: too big", 413))).ask("x", QUESTION)


def test_with_no_key_set_asking_raises_no_key_naming_the_variable():
    with pytest.raises(NoKey) as caught:
        model(None).ask("x", QUESTION)
    assert caught.value.variable == KEY


def test_the_body_is_the_request_the_service_receives_as_json_with_no_key():
    body = json.loads(model(None).body("class A: ...\n", QUESTION))
    assert body == {"model": "jev-1.14.0", "state": "class A: ...\n", "questions": {NAME: {
        "type": "choice", "instructions": "Which part?",
        "criteria": {"domain": "Is it a value?", "main": "starts the app"}}}}


YES_OR_NO = Choice("Does it decide the rule itself?", (Option("yes", "it tests the fields"), Option("no", "")), YES_NO)
LEVELS = Choice("How far does it reach?", tuple(Option(str(n), f"level {n}") for n in range(5)), SCORE)


def test_a_yes_or_no_is_sent_as_a_noul_its_yes_as_true_and_read_back_as_the_probability_of_yes_and_of_no():
    client = Client(Response("jev-1.14.0", {NAME: NoulAnswer(0.75)}, Usage(300, 1)))
    assert model(client).ask("def a(): ...\n", YES_OR_NO) == Answer("jev-1.14.0", (("yes", 0.75), ("no", 0.25)), 300, 1)
    assert client.asked == [("def a(): ...\n", {NAME: NoulQuestion("Does it decide the rule itself?",
                                                                   "it tests the fields", None)})]


def test_a_score_is_sent_as_its_levels_in_order_and_read_back_as_the_probability_of_each_level():
    answer = ScoreAnswer(2.5, 0.6, {str(n): f"level {n}" for n in range(5)}, {"2": 0.5, "3": 0.5})
    client = Client(Response("jev-1.14.0", {NAME: answer}, Usage(300, 1)))
    assert model(client).ask("x", LEVELS).probabilities == (("0", 0.0), ("1", 0.0), ("2", 0.5), ("3", 0.5), ("4", 0.0))
    assert client.asked[0][1] == {NAME: ScoreQuestion([f"level {n}" for n in range(5)], "How far does it reach?")}


def test_the_body_of_a_yes_or_no_and_of_a_score_is_what_the_service_receives():
    noul = json.loads(model(None).body("x", YES_OR_NO))["questions"][NAME]
    score = json.loads(model(None).body("x", LEVELS))["questions"][NAME]
    assert noul == {"type": "noul", "instructions": "Does it decide the rule itself?",
                    "criteria": {"true": "it tests the fields"}}
    assert score == {"type": "score", "instructions": "How far does it reach?",
                     "criteria": [f"level {n}" for n in range(5)]}
