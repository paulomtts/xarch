"""In-memory implementations of the review module's ports. Not adapters: test doubles only."""
from __future__ import annotations

from pathlib import Path

from xarch.kernel.source import CommentSpan
from xarch.modules.review.domain.errors import NoKey, NotAccepted, Refused, Unanswered
from xarch.modules.review.domain.published import Choice, PlacementHeld, Sender
from xarch.modules.review.domain.values import Answer, Calibration, CodeFile, Found, Read, Reads, Words


class FakeCode:
    """Satisfies review's Code: the files found at each path, by the path as given (a path given nowhere finds
    nothing), the files of the paths joined in order; a path listed as refused raises Refused with its reason;
    where the comments of a text an eval reads lie, by the text (none for any other); and the parts whose `holds` a
    text would break, by the text (none for any other), each set of files asked of recorded with the app and the root
    they were asked with."""

    def __init__(self, found: dict[str, Found], refused: dict[str, str] | None = None,
                 reads: dict[tuple[str, str], tuple[Read, ...]] | None = None,
                 comments: dict[str, tuple[CommentSpan, ...]] | None = None,
                 breaks: dict[str, tuple[str, ...]] | None = None):
        self._found, self._refused, self._reads = found, dict(refused or {}), dict(reads or {})
        self._comments, self._breaks = dict(comments or {}), dict(breaks or {})
        self.asked: list[tuple[str, tuple[str, ...]]] = []
        self.held: list[tuple[str, tuple[str, ...], Path | None]] = []

    def files(self, paths: tuple[Path, ...], cwd: Path, app: Path, profile: str, tests: Path | None) -> Found:
        for path in paths:
            if path.as_posix() in self._refused:
                raise Refused(self._refused[path.as_posix()])
        each = [self._found.get(path.as_posix(), Found(())) for path in paths]
        return Found(tuple(file for f in each for file in f.read), tuple(item for f in each for item in f.unread))

    def reads(self, profile: str, app: str, asked: str, files: tuple[tuple[str, str], ...]) -> tuple[Reads, ...]:
        """What the eval reads in each file, by the eval and the file's text: the file whole when none is set; the
        paths each eval was asked of recorded."""
        self.asked.append((asked, tuple(path for path, _ in files)))
        return tuple(Reads(CodeFile(path, "", text, comments=self._comments.get(text, ())),
                           self._reads.get((asked, text), (Read((0, 0), ""),))) for path, text in files)

    def breaks(self, profile: str, app: str, files: tuple[tuple[str, str], ...],
               root: Path | None = None) -> tuple[tuple[str, ...], ...]:
        self.held.append((app, tuple(path for path, _ in files), root))
        return tuple(self._breaks.get(text, ()) for _, text in files)


class FakeProfile:
    """Satisfies review's Profile: fixed words per profile; a profile listed as refused raises Refused with its
    reason, and one listed as unreadable raises it only when its examples are read."""

    def __init__(self, words: dict[str, Words], refused: dict[str, str] | None = None,
                 examples: dict[str, tuple[tuple[CodeFile, ...], tuple[CodeFile, ...]]] | None = None,
                 unreadable: dict[str, str] | None = None):
        self._words, self._refused, self._examples = words, dict(refused or {}), dict(examples or {})
        self._unreadable = dict(unreadable or {})

    def words(self, profile: str) -> Words:
        if profile in self._refused:
            raise Refused(self._refused[profile])
        return self._words[profile]

    def examples(self, profile: str) -> tuple[tuple[CodeFile, ...], tuple[CodeFile, ...]]:
        """The files placement is held to, the clean ones and the flagged ones; none when none are set."""
        if profile in self._refused:
            raise Refused(self._refused[profile])
        if profile in self._unreadable:
            raise Refused(self._unreadable[profile])
        return self._examples.get(profile, ((), ()))


class FakeDecisionModel:
    """Satisfies review's DecisionModel: the answer to each text by the text and the name of the question's first
    option, else by the text alone, every question asked recorded; a question with no answer (or None by its order)
    raises Unanswered with reason, one about a text in refused NotAccepted with the words given for it; asking with
    keyed False raises NoKey, and with a key that cannot be used (unusable, why, is not "") Refused, the question
    recorded as tried."""

    def __init__(self, answers: dict[str, Answer], keyed: bool = True, reason: str = "the decision model failed",
                 by_order: dict[tuple[str, str], Answer | None] | None = None, refused: dict[str, str] | None = None,
                 unusable: str = ""):
        self._answers, self._keyed, self._reason, self._by_order = answers, keyed, reason, dict(by_order or {})
        self._refused, self._unusable = dict(refused or {}), unusable
        self.asked: list[str] = []
        self.tried: list[str] = []

    def sends(self) -> Sender:
        return Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", self._keyed, self._unusable)

    def body(self, text: str, question: Choice) -> str:
        return f"{question.ask} {len(question.options)} {text}"

    def ask(self, text: str, question: Choice) -> Answer:
        if not self._keyed:
            raise NoKey("MODEL_KEY")
        if self._unusable:
            self.tried.append(text)
            raise Refused(f"MODEL_KEY cannot be used: {self._unusable}")
        self.asked.append(text)
        if text in self._refused:
            raise NotAccepted(self._refused[text])
        answer = self._by_order.get((text, question.options[0].name), self._answers.get(text))
        if answer is None:
            raise Unanswered(self._reason)
        return answer


class FakeAnswers:
    """Satisfies review's Answers: the answers kept, by folder and key; every answer kept here recorded; a folder in
    unready cannot keep answers, and is refused with its reason."""

    def __init__(self, kept: dict[tuple[Path, str], Answer] | None = None, unready: dict[Path, str] | None = None):
        self.kept, self._unready = dict(kept or {}), dict(unready or {})

    def ready(self, folder: Path) -> None:
        if folder in self._unready:
            raise Refused(self._unready[folder])

    def get(self, folder: Path, key: str) -> Answer | None:
        return self.kept.get((folder, key))

    def put(self, folder: Path, key: str, answer: Answer) -> None:
        self.kept[(folder, key)] = answer


class FakeCalibrations:
    """Satisfies review's Calibrations: the evals recorded, and placement, by the record's path; every record put kept
    here."""

    def __init__(self, kept: dict[Path, dict[str, Calibration]] | None = None,
                 placed: dict[Path, PlacementHeld] | None = None):
        self.kept = {path: dict(held) for path, held in (kept or {}).items()}
        self.placed = dict(placed or {})

    def placement(self, record: Path) -> PlacementHeld | None:
        return self.placed.get(record)

    def put_placement(self, record: Path, held: PlacementHeld) -> None:
        self.placed[record] = held

    def get(self, record: Path) -> dict[str, Calibration]:
        return dict(self.kept.get(record, {}))

    def put(self, record: Path, held: dict[str, Calibration]) -> None:
        self.kept[record] = dict(held)
