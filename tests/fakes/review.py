"""In-memory implementations of the review module's ports. Not adapters: test doubles only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import Found, Words


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
