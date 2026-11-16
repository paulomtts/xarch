"""In-memory implementations of the review module's ports. Not adapters: test doubles only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.review.domain.errors import NoKey, Refused, Unanswered
from xarch.modules.review.domain.published import Choice, Sender
from xarch.modules.review.domain.values import Answer, Found, Words


class FakeCode:
    """Satisfies review's Code: the files found at each path, by the path as given (a path given nowhere finds
    nothing), the files of the paths joined in order; a path listed as refused raises Refused with its reason."""

    def __init__(self, found: dict[str, Found], refused: dict[str, str] | None = None):
        self._found, self._refused = found, dict(refused or {})

    def files(self, paths: tuple[Path, ...], cwd: Path, app: Path, profile: str, tests: Path | None) -> Found:
        for path in paths:
            if path.as_posix() in self._refused:
                raise Refused(self._refused[path.as_posix()])
        each = [self._found.get(path.as_posix(), Found(())) for path in paths]
        return Found(tuple(file for f in each for file in f.read), tuple(item for f in each for item in f.unread))


class FakeProfile:
    """Satisfies review's Profile: fixed words per profile; a profile listed as refused raises Refused with its
    reason."""

    def __init__(self, words: dict[str, Words], refused: dict[str, str] | None = None):
        self._words, self._refused = words, dict(refused or {})

    def words(self, profile: str) -> Words:
        if profile in self._refused:
            raise Refused(self._refused[profile])
        return self._words[profile]


class FakeDecisionModel:
    """Satisfies review's DecisionModel: the answer to each text by the text, every question asked recorded; a text
    with no answer raises Unanswered with reason; asking with keyed False raises NoKey."""

    def __init__(self, answers: dict[str, Answer], keyed: bool = True, reason: str = "the decision model failed"):
        self._answers, self._keyed, self._reason = answers, keyed, reason
        self.asked: list[str] = []

    def sends(self) -> Sender:
        return Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", self._keyed)

    def body(self, text: str, question: Choice) -> str:
        return f"{question.ask} {len(question.options)} {text}"

    def ask(self, text: str, question: Choice) -> Answer:
        if not self._keyed:
            raise NoKey("MODEL_KEY")
        self.asked.append(text)
        if text not in self._answers:
            raise Unanswered(self._reason)
        return self._answers[text]


class FakeAnswers:
    """Satisfies review's Answers: the answers kept, by folder and key; every answer kept here recorded."""

    def __init__(self, kept: dict[tuple[Path, str], Answer] | None = None):
        self.kept = dict(kept or {})

    def get(self, folder: Path, key: str) -> Answer | None:
        return self.kept.get((folder, key))

    def put(self, folder: Path, key: str, answer: Answer) -> None:
        self.kept[(folder, key)] = answer
