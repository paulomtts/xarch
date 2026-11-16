"""A client for TypeSafe's decision model, Jev: questions about a state, each with one answer out of several options, go
out, and the probability of each option comes back. Knows no module.

Whatever is given as the state and in the questions leaves the machine: it is sent as it is to TypeSafe's service, over
the network. Nothing else is sent: no telemetry, and only the headers the API needs and the plain User-Agent `xarch`.

The key is given to the client, never read from the environment or a file, and it appears in no error, no repr and no
message: where TypeSafe echoes it back, it is cut out. A busy service (429, 529) is retried with a growing wait; any
other failure is raised at once as a TypeSafeError. The limits the docs state are checked before any call.
"""
from __future__ import annotations

import json
import math
import mimetypes
import socket
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from http.client import HTTPException
from typing import Any

URL = "https://api.typesafe.ai"
"""Where TypeSafe's decision model answers."""
MAX_OPTIONS = 255
FIRST_WAIT = 0.5
LONGEST_WAIT = 60.0
BUSY = (429, 529)


@dataclass(frozen=True)
class _FieldProblem:
    """One field TypeSafe named as wrong, as a dotted path, and why."""

    field: str
    message: str


class TypeSafeError(Exception):
    """Something went wrong with a call; status is TypeSafe's HTTP status, or None when none was received, and
    retryable says whether trying the same call again later could succeed."""

    def __init__(self, message: str, status: int | None = None, problems: Sequence[_FieldProblem] = (),
                 retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.problems = tuple(problems)
        self.retryable = retryable


class AuthenticationError(TypeSafeError):
    """The key is missing or not accepted (401)."""


class InvalidRequestError(TypeSafeError):
    """The request breaks a rule: caught here before any call (no status), or refused by TypeSafe (400, 413, 415, 422),
    where problems names the fields of a 422."""


class RateLimitedError(TypeSafeError):
    """TypeSafe was rate-limiting (429) or overloaded (529) on every try, retries included."""


class UnreachableError(TypeSafeError):
    """The service could not be reached, or did not answer in time (timed_out)."""

    def __init__(self, message: str, timed_out: bool = False):
        super().__init__(message, retryable=True)
        self.timed_out = timed_out


class UnexpectedResponseError(TypeSafeError):
    """TypeSafe answered with a status, or a body, that the documentation does not describe."""


def _invalid(message: str) -> InvalidRequestError:
    return InvalidRequestError(message)


def _text(value: Any, what: str, optional: bool = True) -> None:
    if value is None and optional:
        return
    if not isinstance(value, str):
        raise _invalid(f"{what} must be text")


@dataclass(frozen=True)
class ChoiceQuestion:
    """One option out of 1 to 255, each a name and its description (None: the name alone says it)."""

    criteria: Mapping[str, str | None]
    instructions: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "criteria", dict(self.criteria))
        if not 1 <= len(self.criteria) <= MAX_OPTIONS:
            raise _invalid(f"a choice question needs 1 to {MAX_OPTIONS} options, not {len(self.criteria)}")
        for name, description in self.criteria.items():
            if not isinstance(name, str) or not name:
                raise _invalid("a choice option needs a name that is text and not empty")
            _text(description, "a choice option's description")
        _text(self.instructions, "a choice question's instructions")

    def body(self) -> dict[str, Any]:
        body: dict[str, Any] = {"type": "choice"}
        if self.instructions is not None:
            body["instructions"] = self.instructions
        body["criteria"] = dict(self.criteria)
        return body


@dataclass(frozen=True)
class ChoiceAnswer:
    """The option chosen, how concentrated the probabilities are (0 to 1) and the probability of each option."""

    choice: str
    confidence: float
    probabilities: Mapping[str, float]


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class Response:
    """The model version that answered, which may differ from the alias asked for, the answers by question name and
    the tokens used."""

    model: str
    answers: Mapping[str, ChoiceAnswer]
    usage: Usage


def build_request(model: str, state: Any, questions: Mapping[str, ChoiceQuestion]) -> dict[str, Any]:
    """The JSON body of a call; raises InvalidRequestError for a limit the docs state or a state that is not JSON."""
    if not isinstance(model, str) or not model:
        raise _invalid("a model name is required")
    if not questions:
        raise _invalid("at least one question is required")
    for name in questions:
        if not isinstance(name, str) or not name:
            raise _invalid("a question needs a name that is text and not empty")
    body = {"model": model, "state": state, "questions": {name: question.body() for name, question in questions.items()}}
    try:
        json.dumps(body, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as e:
        raise _invalid(f"the state is not plain JSON data: {e}") from e
    return body


def _unexpected(what: str, status: int | None = 200) -> UnexpectedResponseError:
    return UnexpectedResponseError(f"TypeSafe's answer is not the documented shape: {what}", status=status)


def _number(value: Any, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise _unexpected(f"{what} is not a number")
    if not 0 <= value <= 1:
        raise _unexpected(f"{what} is not between 0 and 1")
    return value


def _probabilities(value: Any, what: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise _unexpected(f"{what} is not an object")
    return {str(k): _number(v, f"{what}.{k}") for k, v in value.items()}


def _object(value: Any, what: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _unexpected(f"{what} is not an object")
    return value


def _field(body: dict[str, Any], key: str, what: str) -> Any:
    if key not in body:
        raise _unexpected(f"{what} has no {key}")
    return body[key]


def _answer(raw: Any, question: ChoiceQuestion, name: str) -> ChoiceAnswer:
    what = f"answer {name}"
    body = _object(raw, what)
    kind = _field(body, "type", what)
    if kind != question.body()["type"]:
        raise _unexpected(f"{what} is of type {kind!r}, not the kind asked")
    confidence = _number(_field(body, "confidence", what), f"{what}.confidence")
    probabilities = _probabilities(_field(body, "probabilities", what), f"{what}.probabilities")
    choice = _field(body, "choice", what)
    if not isinstance(choice, str):
        raise _unexpected(f"{what}.choice is not text")
    return ChoiceAnswer(choice, confidence, probabilities)


def _read_response(body: Any, questions: Mapping[str, ChoiceQuestion]) -> Response:
    """The Response in a call's JSON body, of the answers to exactly these questions; raises UnexpectedResponseError."""
    top = _object(body, "the body")
    model = _field(top, "model", "the body")
    if not isinstance(model, str):
        raise _unexpected("model is not text")
    usage = _object(_field(top, "usage", "the body"), "usage")
    tokens = []
    for key in ("input_tokens", "output_tokens"):
        count = _field(usage, key, "usage")
        if isinstance(count, bool) or not isinstance(count, int):
            raise _unexpected(f"usage.{key} is not a whole number")
        tokens.append(count)
    raw = _object(_field(top, "answers", "the body"), "answers")
    if set(raw) != set(questions):
        raise _unexpected(f"the answers are for {sorted(raw)}, the questions were {sorted(questions)}")
    answers = {name: _answer(raw[name], question, name) for name, question in questions.items()}
    return Response(model, answers, Usage(tokens[0], tokens[1]))


def _problems(detail: Any) -> tuple[_FieldProblem, ...]:
    if not isinstance(detail, list):
        return ()
    found = []
    for item in detail:
        if isinstance(item, dict) and isinstance(item.get("loc"), list) and isinstance(item.get("msg"), str):
            found.append(_FieldProblem(".".join(str(part) for part in item["loc"]), item["msg"]))
    return tuple(found)


def _said(text: str) -> tuple[str, tuple[_FieldProblem, ...]]:
    try:
        detail = json.loads(text).get("detail")
    except (ValueError, AttributeError):
        return " ".join(text.split())[:200], ()
    problems = _problems(detail)
    if problems:
        return "; ".join(f"{p.field}: {p.message}" for p in problems), problems
    if isinstance(detail, str):
        return detail, ()
    if detail is None:
        return " ".join(text.split())[:200], ()
    return json.dumps(detail, separators=(",", ":"))[:200], ()


def _wait(retry_after: str | None, attempt: int) -> float:
    try:
        asked = float(retry_after) if retry_after is not None else None
    except ValueError:
        asked = None
    if asked is not None and math.isfinite(asked) and asked >= 0:
        return min(asked, LONGEST_WAIT)
    return min(FIRST_WAIT * 2**attempt, LONGEST_WAIT)


@dataclass
class _Reply:
    status: int
    text: str
    retry_after: str | None = None
    problems: tuple[_FieldProblem, ...] = field(default=())


class TypeSafe:
    """The client: one key, one service. Construct it with the key; it never looks for one itself."""

    def __init__(self, api_key: str, base_url: str = URL, model: str = "jev-latest",
                 timeout: float = 60.0, retries: int = 3, sleep: Callable[[float], None] = time.sleep):
        """timeout is in seconds, per try; retries is how many more tries a busy service gets, with sleep as the wait."""
        if not isinstance(api_key, str) or not api_key:
            raise _invalid("an API key is required")
        if retries < 0:
            raise _invalid("retries cannot be negative")
        if timeout <= 0:
            raise _invalid("the timeout must be more than zero")
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._retries = retries
        self._sleep = sleep

    def __repr__(self) -> str:
        return f"TypeSafe(base_url={self._base!r}, model={self._model!r})"

    def ask(self, state: Any, questions: Mapping[str, ChoiceQuestion]) -> Response:
        """The answers to the questions about the state, which is sent as given: a string, an object or an array of JSON
        values; raises a TypeSafeError."""
        body = build_request(self._model, state, questions)
        return _read_response(self._call("POST", "/v1/systemone", json.dumps(body).encode()), questions)

    def _call(self, method: str, path: str, payload: bytes | None) -> Any:
        attempt = 0
        while True:
            reply = self._once(method, path, payload)
            if reply.status == 200:
                return self._json(reply)
            if reply.status in BUSY and attempt < self._retries:
                self._sleep(_wait(reply.retry_after, attempt))
                attempt += 1
                continue
            raise self._refusal(reply)

    def _json(self, reply: _Reply) -> Any:
        try:
            return json.loads(reply.text)
        except ValueError as e:
            raise _unexpected("the body is not JSON") from e

    def _once(self, method: str, path: str, payload: bytes | None) -> _Reply:
        request = urllib.request.Request(self._base + path, data=payload, method=method, headers={
            "Authorization": f"Bearer {self._key}", "Content-Type": mimetypes.types_map[".json"], "User-Agent": "xarch"})
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                return _Reply(response.status, response.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            with e:
                return _Reply(e.code, e.read().decode("utf-8", "replace"), e.headers.get("Retry-After"))
        except (TimeoutError, socket.timeout) as e:
            raise UnreachableError("TypeSafe did not answer in time", timed_out=True) from e
        except urllib.error.URLError as e:
            timed_out = isinstance(e.reason, TimeoutError)
            reason = "did not answer in time" if timed_out else f"could not be reached: {self._clean(str(e.reason))}"
            raise UnreachableError(f"TypeSafe {reason}", timed_out=timed_out) from e
        except (OSError, HTTPException) as e:
            raise UnreachableError(f"TypeSafe could not be reached: {self._clean(type(e).__name__)}") from e

    def _clean(self, text: str) -> str:
        return text.replace(self._key, "***")

    def _refusal(self, reply: _Reply) -> TypeSafeError:
        said, problems = _said(self._clean(reply.text))
        message = f"TypeSafe answered {reply.status}: {said}"
        if reply.status in BUSY:
            return RateLimitedError(message, reply.status, retryable=True)
        if reply.status == 401:
            return AuthenticationError(message, reply.status)
        if reply.status in (400, 413, 415, 422):
            return InvalidRequestError(message, reply.status, problems)
        return UnexpectedResponseError(message, reply.status, retryable=reply.status >= 500)
