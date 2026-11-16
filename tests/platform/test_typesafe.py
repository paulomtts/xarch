"""The TypeSafe client: the request body each question kind makes, each answer kind read back, the retries on a busy
service, and every failure named, with the key in none of them. Served by a local server, never the network."""
import json

import pytest

from tests.platform.conftest import Reply
from xarch.platform.typesafe import (
    AuthenticationError,
    ChoiceAnswer,
    ChoiceQuestion,
    InvalidRequestError,
    NoulAnswer,
    NoulQuestion,
    RateLimitedError,
    ScoreAnswer,
    ScoreQuestion,
    TypeSafe,
    TypeSafeError,
    UnexpectedResponseError,
    UnreachableError,
    Usage,
    build_request,
)

KEY = "sk-secret-key-123"
USAGE = {"input_tokens": 12, "output_tokens": 3}
CHOICE = {"type": "choice", "choice": "pass", "confidence": 0.8, "probabilities": {"pass": 0.9, "fail": 0.1}}
PASS = ChoiceAnswer(choice="pass", confidence=0.8, probabilities={"pass": 0.9, "fail": 0.1})
NOUL = {"type": "noul", "noul": 0.9}
SCORE = {"type": "score", "score": 1.4, "confidence": 0.6, "legend": {"0": "bad", "1": "ok", "2": "good"},
         "probabilities": {"0": 0.1, "1": 0.4, "2": 0.5}}


def asked() -> ChoiceQuestion:
    """A question of two options, each named only."""
    return ChoiceQuestion({"pass": None, "fail": None})


def answered(**answers):
    return {"model": "jev-1.13.0", "answers": answers, "usage": USAGE}


def client(server, **options):
    waits = options.pop("waits", [])
    return TypeSafe(KEY, base_url=server.url, sleep=waits.append, **options)


@pytest.mark.parametrize("question, body", [
    pytest.param(ChoiceQuestion({"a": "first", "b": None}, "Pick."),
                 {"type": "choice", "instructions": "Pick.", "criteria": {"a": "first", "b": None}},
                 id="a choice question sends its options, a bare name as null"),
    pytest.param(ChoiceQuestion({"a": "first"}), {"type": "choice", "criteria": {"a": "first"}},
                 id="a choice question with no instructions sends its options alone"),
    pytest.param(NoulQuestion(), {"type": "noul"}, id="a noul question with nothing else is its type alone"),
    pytest.param(NoulQuestion("Is it safe?", true="safe", false="unsafe"),
                 {"type": "noul", "instructions": "Is it safe?", "criteria": {"true": "safe", "false": "unsafe"}},
                 id="a noul question with instructions and both criteria"),
    pytest.param(NoulQuestion(true="safe"), {"type": "noul", "criteria": {"true": "safe"}},
                 id="a noul question with one criterion sends only that one"),
    pytest.param(ScoreQuestion(["bad", "ok", "good"]), {"type": "score", "criteria": ["bad", "ok", "good"]},
                 id="a score question sends its levels in order"),
    pytest.param(ScoreQuestion(["bad", "good"], "Rate it."),
                 {"type": "score", "instructions": "Rate it.", "criteria": ["bad", "good"]},
                 id="a score question sends its instructions before its levels"),
])
def test_the_request_body_of_a_question(question, body):
    assert build_request("jev-latest", {"file": "x"}, {"q": question}) == {
        "model": "jev-latest", "state": {"file": "x"}, "questions": {"q": body}}


def test_several_questions_travel_in_one_body_under_the_names_chosen():
    request = build_request("jev-latest", "text", {"one": asked(), "two": ChoiceQuestion({"a": None})})
    assert list(request["questions"]) == ["one", "two"]
    assert request["state"] == "text"


@pytest.mark.parametrize("state", [
    pytest.param("text", id="a string"),
    pytest.param({"a": [1, 2.5, None, True]}, id="an object"),
    pytest.param(["x", {"y": 1}], id="an array"),
])
def test_the_state_goes_as_given(state):
    assert build_request("m", state, {"q": asked()})["state"] == state


@pytest.mark.parametrize("build", [
    pytest.param(lambda: ChoiceQuestion({}), id="a choice with no options"),
    pytest.param(lambda: ChoiceQuestion({str(i): None for i in range(256)}), id="a choice with 256 options"),
    pytest.param(lambda: ChoiceQuestion({"": None}), id="a choice option with an empty name"),
    pytest.param(lambda: ChoiceQuestion({"a": 3}), id="a choice option's description that is not text"),
    pytest.param(lambda: ChoiceQuestion({"a": None}, 3), id="a choice question's instructions that are not text"),
    pytest.param(lambda: ScoreQuestion([]), id="a score with no levels"),
    pytest.param(lambda: ScoreQuestion([str(i) for i in range(11)]), id="a score with 11 levels"),
    pytest.param(lambda: ScoreQuestion(["ok", 3]), id="a score level that is not text"),
    pytest.param(lambda: NoulQuestion(true=3), id="a noul criterion that is not text"),
    pytest.param(lambda: build_request("m", "s", {}), id="no question at all"),
    pytest.param(lambda: build_request("m", "s", {"": asked()}), id="a question with an empty name"),
    pytest.param(lambda: build_request("", "s", {"q": asked()}), id="no model"),
    pytest.param(lambda: build_request("m", {"x": float("nan")}, {"q": asked()}), id="a state that is not JSON"),
    pytest.param(lambda: build_request("m", object(), {"q": asked()}), id="a state of a type JSON lacks"),
])
def test_a_request_that_breaks_a_documented_limit_is_refused_before_any_call(build):
    with pytest.raises(InvalidRequestError) as caught:
        build()
    assert caught.value.status is None and caught.value.retryable is False


def test_the_limits_are_inclusive():
    assert ChoiceQuestion({str(i): None for i in range(255)})
    assert ChoiceQuestion({"only": None})
    assert ScoreQuestion([str(i) for i in range(10)])
    assert ScoreQuestion(["only"])


def test_a_refused_request_makes_no_call(server):
    with pytest.raises(InvalidRequestError):
        client(server).ask("s", {})
    assert server.requests == []


def test_the_request_path_headers_and_body_are_exactly_what_the_api_needs(server):
    server.script(Reply(body=answered(q=CHOICE)))
    client(server).ask({"f": 1}, {"q": ChoiceQuestion({"pass": None}, "Is it?")})
    (sent,) = server.requests
    assert (sent.method, sent.path) == ("POST", "/v1/systemone")
    assert json.loads(sent.body) == {"model": "jev-latest", "state": {"f": 1},
                                     "questions": {"q": {"type": "choice", "instructions": "Is it?",
                                                         "criteria": {"pass": None}}}}
    assert sent.headers["authorization"] == f"Bearer {KEY}"
    assert sent.headers["content-type"] == "application/json"
    assert sent.headers["user-agent"] == "xarch"
    assert set(sent.headers) == {"authorization", "content-type", "user-agent", "host", "content-length", "connection",
                                    "accept-encoding"}


def test_the_model_asked_for_is_the_one_sent(server):
    server.script(Reply(body=answered(q=CHOICE)))
    client(server, model="jev-1.13.0").ask("s", {"q": asked()})
    assert json.loads(server.requests[0].body)["model"] == "jev-1.13.0"


def test_each_answer_is_read_into_its_type_with_the_model_that_answered_and_the_usage(server):
    server.script(Reply(body=answered(c=CHOICE, d=dict(CHOICE, choice="fail"))))
    response = client(server).ask("s", {"c": asked(), "d": asked()})
    assert response.model == "jev-1.13.0"
    assert response.usage == Usage(input_tokens=12, output_tokens=3)
    assert response.answers == {"c": PASS, "d": ChoiceAnswer(choice="fail", confidence=0.8,
                                                             probabilities={"pass": 0.9, "fail": 0.1})}


def test_an_integer_probability_is_read_as_a_number(server):
    server.script(Reply(body=answered(c=dict(CHOICE, probabilities={"pass": 1, "fail": 0}, confidence=1))))
    answer = client(server).ask("s", {"c": asked()}).answers["c"]
    assert (answer.probabilities, answer.confidence) == ({"pass": 1, "fail": 0}, 1)


@pytest.mark.parametrize("status, body, error, problems", [
    pytest.param(401, {"detail": "Invalid API key"}, AuthenticationError, (), id="a bad key"),
    pytest.param(400, {"detail": "max_tokens_exceeded"}, InvalidRequestError, (), id="a request rule broken, detail text"),
    pytest.param(400, {"detail": {"code": "max_tokens_exceeded"}}, InvalidRequestError, (),
                 id="a request rule broken, detail object"),
    pytest.param(413, {"detail": "too big"}, InvalidRequestError, (), id="a body over the size limit"),
    pytest.param(415, {"detail": "bad encoding"}, InvalidRequestError, (), id="an unsupported encoding"),
    pytest.param(422, {"detail": [{"loc": ["body", "questions", "q", "choice", "criteria"], "msg": "Field required",
                                   "type": "missing"}]},
                 InvalidRequestError, (("body.questions.q.choice.criteria", "Field required"),),
                 id="a validation failure names its field"),
    pytest.param(422, {"detail": [{"loc": ["body", "questions", 0], "msg": "bad", "type": "x"},
                                  {"loc": ["body", "model"], "msg": "Field required", "type": "missing"}]},
                 InvalidRequestError, (("body.questions.0", "bad"), ("body.model", "Field required")),
                 id="every field a validation failure names"),
])
def test_a_refusal_is_its_own_error_naming_what_typesafe_said(server, status, body, error, problems):
    server.script(Reply(status, body))
    with pytest.raises(error) as caught:
        client(server).ask("s", {"q": asked()})
    assert caught.value.status == status
    assert [(p.field, p.message) for p in caught.value.problems] == list(problems)
    assert caught.value.retryable is False
    assert len(server.requests) == 1


def test_a_422_message_carries_the_field_and_the_reason(server):
    server.script(Reply(422, {"detail": [{"loc": ["body", "model"], "msg": "Field required", "type": "missing"}]}))
    with pytest.raises(InvalidRequestError, match=r"body\.model: Field required"):
        client(server).ask("s", {"q": asked()})


def test_a_400_message_carries_what_was_said(server):
    server.script(Reply(400, {"detail": "max_tokens_exceeded"}))
    with pytest.raises(InvalidRequestError, match="max_tokens_exceeded"):
        client(server).ask("s", {"q": asked()})


@pytest.mark.parametrize("status", [
    pytest.param(429, id="rate-limited"),
    pytest.param(529, id="overloaded"),
])
def test_a_busy_service_is_retried_and_the_next_answer_is_used(server, status):
    waits = []
    server.script(Reply(status, {"detail": "busy"}), Reply(body=answered(q=CHOICE)))
    response = client(server, waits=waits).ask("s", {"q": asked()})
    assert response.answers == {"q": PASS}
    assert len(server.requests) == 2 and len(waits) == 1


@pytest.mark.parametrize("status", [
    pytest.param(429, id="rate-limited"),
    pytest.param(529, id="overloaded"),
])
def test_a_busy_service_until_the_retries_run_out_is_rate_limited_after_one_more_try_than_retries(server, status):
    waits = []
    server.script(*[Reply(status, {"detail": "busy"})] * 4)
    with pytest.raises(RateLimitedError) as caught:
        client(server, waits=waits, retries=2).ask("s", {"q": asked()})
    assert (caught.value.status, caught.value.retryable) == (status, True)
    assert len(server.requests) == 3 and len(waits) == 2


def test_with_no_retries_the_first_busy_answer_is_the_error(server):
    server.script(Reply(429, {"detail": "busy"}))
    with pytest.raises(RateLimitedError):
        client(server, retries=0).ask("s", {"q": asked()})
    assert len(server.requests) == 1


def test_the_wait_doubles_between_retries_without_a_retry_after(server):
    waits = []
    server.script(*[Reply(429, {"detail": "busy"})] * 4)
    with pytest.raises(RateLimitedError):
        client(server, waits=waits, retries=3).ask("s", {"q": asked()})
    assert waits == [0.5, 1.0, 2.0]


def test_a_retry_after_is_the_wait_when_the_service_sends_one(server):
    waits = []
    server.script(Reply(429, {"detail": "busy"}, {"Retry-After": "7"}), Reply(529, {"detail": "busy"}),
                  Reply(body=answered(q=CHOICE)))
    client(server, waits=waits).ask("s", {"q": asked()})
    assert waits == [7.0, 1.0]


@pytest.mark.parametrize("header", [
    pytest.param("soon", id="text"),
    pytest.param("-5", id="a negative number"),
    pytest.param("Wed, 21 Oct 2026 07:28:00 GMT", id="a date"),
])
def test_a_retry_after_that_is_no_usable_number_of_seconds_is_ignored(server, header):
    waits = []
    server.script(Reply(429, {"detail": "busy"}, {"Retry-After": header}), Reply(body=answered(q=CHOICE)))
    client(server, waits=waits).ask("s", {"q": asked()})
    assert waits == [0.5]


def test_a_retry_after_past_the_longest_wait_is_cut_to_it(server):
    waits = []
    server.script(Reply(429, {"detail": "busy"}, {"Retry-After": "86400"}), Reply(body=answered(q=CHOICE)))
    client(server, waits=waits).ask("s", {"q": asked()})
    assert waits == [60.0]


def test_a_service_that_cannot_be_reached_is_unreachable(unused_url):
    with pytest.raises(UnreachableError) as caught:
        TypeSafe(KEY, base_url=unused_url, sleep=lambda s: None).ask("s", {"q": asked()})
    assert (caught.value.status, caught.value.retryable, caught.value.timed_out) == (None, True, False)


def test_a_service_that_does_not_answer_in_time_is_unreachable_and_timed_out(server):
    server.script(Reply(stall=True))
    with pytest.raises(UnreachableError) as caught:
        client(server, timeout=0.2).ask("s", {"q": asked()})
    assert (caught.value.retryable, caught.value.timed_out) == (True, True)


@pytest.mark.parametrize("reply", [
    pytest.param(Reply(raw=b"<html>not json</html>"), id="a body that is not JSON"),
    pytest.param(Reply(body=["a list"]), id="a body that is not an object"),
    pytest.param(Reply(body={"model": "m", "usage": USAGE}), id="no answers"),
    pytest.param(Reply(body={"answers": {"q": CHOICE}, "usage": USAGE}), id="no model"),
    pytest.param(Reply(body={"model": "m", "answers": {"q": CHOICE}}), id="no usage"),
    pytest.param(Reply(body={"model": "m", "answers": {"q": CHOICE}, "usage": {"input_tokens": 1}}), id="half a usage"),
    pytest.param(Reply(body={"model": "m", "answers": {"q": CHOICE}, "usage": {"input_tokens": "1", "output_tokens": 2}}),
                 id="a token count that is text"),
    pytest.param(Reply(body=answered(q={key: value for key, value in CHOICE.items() if key != "probabilities"})),
                 id="a choice answer with no probabilities"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, probabilities={"pass": 1.5}))), id="a probability above 1"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, probabilities={"pass": True}))), id="a probability that is a boolean"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, choice=3))), id="a choice that is not text"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, confidence=None))), id="a choice with no confidence"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, probabilities=[0.5]))), id="probabilities that are not a mapping"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, probabilities={"pass": "high"}))), id="a probability that is text"),
    pytest.param(Reply(body=answered(q={"type": "box", "box": {}, "confidence": 1})), id="a kind this client does not ask"),
    pytest.param(Reply(body=answered(q={key: value for key, value in CHOICE.items() if key != "type"})),
                 id="an answer with no type"),
    pytest.param(Reply(body=answered(other=CHOICE)), id="an answer for a question not asked"),
    pytest.param(Reply(body=answered(q=dict(CHOICE, type="noul"))), id="an answer of another kind than its question"),
    pytest.param(Reply(body={"model": "m", "answers": {}, "usage": USAGE}), id="no answer for the question asked"),
])
def test_a_200_that_is_not_the_documented_shape_is_an_unexpected_response(server, reply):
    server.script(reply)
    with pytest.raises(UnexpectedResponseError) as caught:
        client(server).ask("s", {"q": asked()})
    assert caught.value.status in (200, None) and caught.value.retryable is False


@pytest.mark.parametrize("reply, question", [
    pytest.param(Reply(body=answered(q={"type": "noul"})), NoulQuestion(), id="a noul answer with no probability"),
    pytest.param(Reply(body=answered(q={"type": "noul", "noul": 1.5})), NoulQuestion(), id="a noul above 1"),
    pytest.param(Reply(body=answered(q={"type": "noul", "noul": True})), NoulQuestion(), id="a noul that is a boolean"),
    pytest.param(Reply(body=answered(q={key: value for key, value in SCORE.items() if key != "score"})),
                 ScoreQuestion(["a"]), id="a score answer with no score"),
    pytest.param(Reply(body=answered(q=dict(SCORE, score="high"))), ScoreQuestion(["a"]), id="a score that is text"),
    pytest.param(Reply(body=answered(q=dict(SCORE, legend=[1]))), ScoreQuestion(["a"]),
                 id="a legend that is not a mapping"),
])
def test_a_yes_or_no_or_a_score_answer_not_of_the_documented_shape_is_an_unexpected_response(server, reply, question):
    server.script(reply)
    with pytest.raises(UnexpectedResponseError):
        client(server).ask("s", {"q": question})


def test_each_answer_kind_is_read_into_its_type_with_the_model_that_answered(server):
    server.script(Reply(body=answered(n=NOUL, c=CHOICE, s=SCORE)))
    response = client(server).ask("s", {"n": NoulQuestion(), "c": asked(), "s": ScoreQuestion(["bad", "ok", "good"])})
    assert response.model == "jev-1.13.0"
    assert response.answers == {
        "n": NoulAnswer(noul=0.9), "c": PASS,
        "s": ScoreAnswer(score=1.4, confidence=0.6, legend={"0": "bad", "1": "ok", "2": "good"},
                         probabilities={"0": 0.1, "1": 0.4, "2": 0.5})}


def test_a_score_above_1_is_a_level_and_an_integer_score_is_read_as_a_number(server):
    score = dict(SCORE, score=2, probabilities={"0": 0, "1": 0, "2": 1}, confidence=1)
    server.script(Reply(body=answered(s=score)))
    answer = client(server).ask("s", {"s": ScoreQuestion(["a", "b", "c"])}).answers["s"]
    assert isinstance(answer, ScoreAnswer) and (answer.score, answer.confidence) == (2, 1)


def test_a_status_the_api_does_not_document_is_an_unexpected_response_naming_it(server):
    server.script(Reply(502, {"detail": "bad gateway"}))
    with pytest.raises(UnexpectedResponseError, match="502") as caught:
        client(server).ask("s", {"q": asked()})
    assert caught.value.status == 502


@pytest.mark.parametrize("status, body", [
    pytest.param(401, {"detail": f"bad key {KEY}"}, id="a key echoed by a 401"),
    pytest.param(400, {"detail": f"rule broken by {KEY}"}, id="a key echoed by a 400"),
    pytest.param(422, {"detail": [{"loc": ["body", KEY], "msg": f"bad {KEY}", "type": "x"}]}, id="a key echoed by a 422"),
    pytest.param(502, {"detail": KEY}, id="a key echoed by an unexpected status"),
])
def test_the_key_is_in_no_error_even_when_typesafe_echoes_it(server, status, body):
    server.script(Reply(status, body))
    with pytest.raises(TypeSafeError) as caught:
        client(server).ask("s", {"q": asked()})
    shown = " ".join([str(caught.value), repr(caught.value), *(f"{p.field} {p.message}" for p in caught.value.problems)])
    assert KEY not in shown


def test_the_key_is_in_no_error_when_the_service_is_unreachable_or_busy(server, unused_url):
    server.script(Reply(429, {"detail": "busy"}))
    with pytest.raises(RateLimitedError) as busy:
        client(server, retries=0).ask("s", {"q": asked()})
    with pytest.raises(UnreachableError) as gone:
        TypeSafe(KEY, base_url=unused_url).ask("s", {"q": asked()})
    assert KEY not in f"{busy.value!r} {busy.value} {gone.value!r} {gone.value}"


def test_the_key_is_not_in_the_client_repr(server):
    assert KEY not in repr(client(server))


def test_every_error_is_a_typesafe_error():
    for error in (AuthenticationError, InvalidRequestError, RateLimitedError, UnreachableError, UnexpectedResponseError):
        assert issubclass(error, TypeSafeError)


def test_a_trailing_slash_on_the_base_url_does_not_double_the_path(server):
    server.script(Reply(body=answered(q=CHOICE)))
    TypeSafe(KEY, base_url=server.url + "/", sleep=lambda s: None).ask("s", {"q": asked()})
    assert server.requests[0].path == "/v1/systemone"


@pytest.mark.parametrize("make", [
    pytest.param(lambda: TypeSafe(""), id="an empty key"),
    pytest.param(lambda: TypeSafe(KEY, retries=-1), id="a negative retry limit"),
    pytest.param(lambda: TypeSafe(KEY, timeout=0), id="a timeout of nothing"),
])
def test_a_client_built_wrongly_is_refused(make):
    with pytest.raises(InvalidRequestError):
        make()
