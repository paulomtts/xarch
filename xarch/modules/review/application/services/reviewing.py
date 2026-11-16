from __future__ import annotations

from xarch.modules.review.application.logic.questions import characters, placement, request, role_only, tokens
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.profile import Parts
from xarch.modules.review.contract import Review, ReviewPlanned
from xarch.modules.review.domain.errors import Unsendable


class ReviewService:
    """Reads the files chosen, and says what placement would ask of each."""

    def __init__(self, code: Code, parts: Parts):
        self._code, self._parts = code, parts

    def review(self, cmd: Review) -> ReviewPlanned:
        """What placement would send for each file judged; raises NoSelection, AllWithOthers, OverCap, Refused, and
        Unsendable for a review that would send."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app)
        files = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        parts = self._parts.parts(cmd.profile)
        question = placement(parts)
        asked = within_cap(judged(files), cmd.max_files)
        if not cmd.dry_run:
            raise Unsendable()
        requests = tuple(request(file, cmd.app.name) for file in asked)
        sent = characters(requests, question)
        return ReviewPlanned(ways(cmd.paths, cmd.listed, cmd.every), len(files.read) + len(files.unread), requests,
                             left_out(files), question, role_only(parts), sent, tokens(sent))
