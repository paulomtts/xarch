"""The app's files read by the rules module: the only file in review that names rules, and it names only rules'
contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import (
    A_TEST,
    EXCLUDED,
    LINK,
    MISSING,
    NOT_SOURCE,
    OUTSIDE,
    UNPLACED,
    LeftOut,
)
from xarch.modules.review.domain.values import CodeFile, Found, Read, Reads, Span
from xarch.modules.rules import contract as rules
from xarch.modules.rules.contract import (
    CheckRefused,
    ChecksCannotRun,
    FactsKept,
    FileKept,
    KeepFacts,
    KeptResult,
    Outside,
    ReadSources,
    SourceRead,
    SourcesRead,
    SourcesResult,
)

_WHY = {rules.NOT_THERE: MISSING, rules.NOT_SOURCE: NOT_SOURCE, rules.IN_TESTS: A_TEST, rules.IN_PROJECT: OUTSIDE,
        rules.EXCLUDED: EXCLUDED, rules.IN_NO_PART: UNPLACED, rules.LINKED_OUT: LINK}
"""Where rules says a file lies, for each place but a part, in review's words for why it is not read."""


class _Rules(Protocol):
    """The little review uses of rules' controller."""

    def sources(self, cmd: ReadSources) -> SourcesResult: ...

    def kept(self, cmd: KeepFacts) -> KeptResult: ...


class RulesCode:
    """Satisfies review's Code port by translating rules' SourcesRead."""

    def __init__(self, rules: _Rules):
        self._rules = rules

    def files(self, paths: tuple[Path, ...], cwd: Path, app: Path, profile: str, tests: Path | None) -> Found:
        """A refusal of rules raises Refused with its reason; a profile whose own checks cannot run, with each
        problem."""
        match self._rules.sources(ReadSources(paths, cwd, app, profile, tests)):
            case SourcesRead(files):
                return Found(tuple(_read(file) for file in files if file.lies == rules.IN_PART),
                             tuple(LeftOut(file.shown, _WHY[file.lies]) for file in files if file.lies != rules.IN_PART))
            case Outside(reason) | CheckRefused(reason):
                raise Refused(reason)
            case ChecksCannotRun(problems):
                raise Refused("; ".join(problems))


    def reads(self, profile: str, app: str, asked: str, files: tuple[tuple[str, str], ...]) -> tuple[Reads, ...]:
        """A refusal of rules raises Refused with its reason, or with each problem of an eval that cannot be read."""
        match self._rules.kept(KeepFacts(profile, app, asked, files)):
            case FactsKept(found):
                texts = dict(files)
                return tuple(_reads(file, texts[file.path]) for file in found)
            case CheckRefused(reason):
                raise Refused(reason)
            case ChecksCannotRun(problems):
                raise Refused("; ".join(problems))


def _reads(file: FileKept, text: str) -> Reads:
    return Reads(CodeFile(file.path, "", text, file.imports, comments=file.comments),
                 tuple(Read((fact.first, fact.last), fact.name) for fact in file.facts))


def _read(file: SourceRead) -> CodeFile:
    return CodeFile(file.shown, file.part, file.text, file.imports, file.error,
                    tuple(Span(piece.kind, piece.name, piece.owner, (piece.first, piece.last)) for piece in file.pieces),
                    file.target, file.comments)
