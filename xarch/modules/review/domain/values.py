"""The values review reads through its ports: the profile's words review reads (its parts as placement offers them,
what review may send, and the evals of its own), and the files found at the paths given, read or not, with their
pieces; what an eval of the profile's own reads in files; the record of the evals held to their examples; and the
pieces as review judges them."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.source import Import, Unparsable
from xarch.modules.review.domain.published import Choice, LeftOut


@dataclass(frozen=True)
class PartText:
    """A part as placement offers it: its name, its folder as the docs show it, its litmus test ("" for none), its
    role, the line below which a file reads as doubtful there, and whether the profile sets that line by hand."""
    name: str
    folder: str
    litmus: str
    role: str
    line: float
    by_hand: bool = False


@dataclass(frozen=True)
class EvalText:
    """An eval of the profile's own as review asks it: its id; its question; the names of the options whose
    probability reads as the fault; the line the profile writes (None: calibration sets it); what is said of a
    reading and what to do, with {file}, {line}, {name} and {value}; its flagged and clean examples, each a file by its
    path below the app with its code; and what it reads, where and passing which filters, as one text, which review
    never reads but holds the eval to as written."""
    asked: str
    question: Choice
    flagged: tuple[str, ...]
    line: float | None = None
    message: str = ""
    fix: str = ""
    flagged_examples: tuple[tuple[str, str], ...] = ()
    clean_examples: tuple[tuple[str, str], ...] = ()
    reads: str = ""


@dataclass(frozen=True)
class Words:
    """What review reads of a profile: its parts, in its order; the paths below the app of the files review never
    sends; the texts it hides before it sends, each as the profile writes it; and the evals of its own, in its order."""
    parts: tuple[PartText, ...]
    never: tuple[str, ...] = ()
    mask: tuple[str, ...] = ()
    evals: tuple[EvalText, ...] = ()


@dataclass(frozen=True)
class Span:
    """A piece of a file as its language's reader cuts it: its kind, as the reader names it (a function, a class, a
    method); its name; the class it is a method of ("" for a piece at the top level); and the first and last lines it
    spans, counted from 1."""
    kind: str
    name: str
    owner: str
    lines: tuple[int, int]


@dataclass(frozen=True)
class CodeFile:
    """A source file of the app in a part, read: the file, as `check` shows it; the part; its text; its imports; how
    it fails to parse (None: it parses); and its pieces, in the order of their first line."""
    file: str
    part: str
    text: str
    imports: tuple[Import, ...] = ()
    error: Unparsable | None = None
    spans: tuple[Span, ...] = ()


@dataclass(frozen=True)
class Section:
    """A piece of a file as review judges it: its name as shown (Class.method for a method; the names joined, for
    small pieces merged); its kind, the first piece's; the first and last lines it spans; its text, masked; and, for a
    method, the text of its class before its first method, sent with it ("" for any other)."""
    name: str
    kind: str
    lines: tuple[int, int]
    text: str
    head: str = ""


@dataclass(frozen=True)
class Found:
    """The files found at the paths given, each once: those read, in a part of the app, and those that are not, each
    with why, both in the order they were found."""
    read: tuple[CodeFile, ...]
    unread: tuple[LeftOut, ...] = ()


@dataclass(frozen=True)
class Answer:
    """What the decision model answered to a question of one answer out of several: the model version that answered,
    the probability of each option by its name, in the order of the question, and the tokens the question and the
    answer cost."""
    model: str
    probabilities: tuple[tuple[str, float], ...]
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class Read:
    """One thing an eval of the profile's own reads in a file: the lines it spans, counted from 1 ((0, 0) for the file
    whole), and its name (Class.method for a method, "" for the file whole)."""
    lines: tuple[int, int]
    name: str


@dataclass(frozen=True)
class Reads:
    """What an eval of the profile's own reads in one file given: the file, by its path below the app as given; its
    imports, as its language's reader reads them; and each thing it reads, in the order of their lines."""
    path: str
    imports: tuple[Import, ...]
    read: tuple[Read, ...]


@dataclass(frozen=True)
class Calibration:
    """An eval of the profile's own as it was held to its examples, as recorded: the hash of what it was held as
    (question, answer, scope, line written and examples); the model asked; the model version that answered; whether it
    passed; its line; the value of each example file, by path, the flagged ones and the clean ones; and what crossed
    when it did not pass. It holds no code and no question."""
    held: str
    model: str
    answered: str
    passed: bool
    line: float
    flagged: tuple[tuple[str, float], ...] = ()
    clean: tuple[tuple[str, float], ...] = ()
    crossed: str = ""


@dataclass(frozen=True)
class Run:
    """The questions of one run so far: the folder the answers are kept in; whether the run may send nothing; the
    answers the decision model gave and those read from the folder, in order; and the decision model's words when it
    failed ("" while it has not), after which nothing more is sent."""
    folder: Path
    offline: bool
    asked: tuple[Answer, ...] = ()
    reused: tuple[Answer, ...] = ()
    failure: str = ""
