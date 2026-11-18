from __future__ import annotations

from xarch.modules.review.application.logic.accepting import digest, reads_as
from xarch.modules.review.application.logic.answers import accepted_file
from xarch.modules.review.application.logic.questions import request
from xarch.modules.review.application.ports.acceptances import Acceptances
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.review.contract import Accept, Accepted, FileAccepted, Removed, Review, ReviewReading
from xarch.modules.review.domain.errors import NoAnswerKept, NoSelection, NoWhy, Undoubted, Unjudged, Unrecorded
from xarch.modules.review.domain.values import AcceptedFile


class AcceptingService:
    """Records the doubtful files a person read and found fine, each with the hash of its code, from a review that
    reads only the answers kept and sends nothing; and takes files out of that record."""

    def __init__(self, reviewing: ReviewService, code: Code, profile: Profile, acceptances: Acceptances):
        self._reviewing, self._code, self._profile, self._acceptances = reviewing, code, profile, acceptances

    def accept(self, cmd: Accept) -> Accepted | Removed:
        """The files at the paths accepted for the reason given, each as its answers kept read (a file accepted already
        whose code is as it was is accepted again, for the new reason), the record rewritten with them; with remove,
        the files at the paths taken out of it. Nothing is ever sent. Raises NoWhy for a reason of whitespace alone,
        NoSelection when the paths find no file, Unjudged for a file review does not judge, NoAnswerKept for one whose
        answer is not kept, Undoubted for one that does not read as doubtful, Unrecorded for a file to take out that
        the record does not name, and OverCap and Refused as a review does, before anything is recorded."""
        record_path = accepted_file(cmd.app)
        record = self._acceptances.get(record_path)
        if cmd.remove:
            return self._remove(cmd, record)
        why = cmd.why.strip()
        if not why:
            raise NoWhy()
        read = self._reviewing.review(Review(cmd.paths, (), False, cmd.cwd, cmd.app, cmd.profile, cmd.tests,
                                             offline=True, cache=cmd.cache))
        if not isinstance(read, ReviewReading):
            raise NoSelection()
        if read.left_out:
            raise Unjudged(read.left_out)
        if unanswered := tuple(item.file for item in read.unasked if not item.piece and not item.asked):
            raise NoAnswerKept(unanswered)
        if settled := tuple(item for item in read.readings if not item.doubtful and item.accepted is None):
            raise Undoubted(settled)
        if not read.readings:
            raise NoSelection()
        found = self._code.files(cmd.paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        mask = self._profile.words(cmd.profile).mask
        codes = {file.file: digest(request(file, cmd.app.name, mask).text) for file in found.read}
        files = tuple(FileAccepted(item.file, item.part, reads_as(item)) for item in read.readings)
        self._acceptances.put(record_path, record | {file.file: AcceptedFile(file.part, file.reads_as, codes[file.file],
                                                                             why) for file in files})
        return Accepted(files, why, record_path)

    def _remove(self, cmd: Accept, record: dict[str, AcceptedFile]) -> Removed:
        """The files at the paths, found or not there, taken out of the record."""
        found = self._code.files(cmd.paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        files = tuple(dict.fromkeys((*(file.file for file in found.read), *(item.file for item in found.unread))))
        if not files:
            raise NoSelection()
        if absent := tuple(file for file in files if file not in record):
            raise Unrecorded(absent)
        self._acceptances.put(accepted_file(cmd.app), {file: entry for file, entry in record.items()
                                                       if file not in files})
        return Removed(files, accepted_file(cmd.app))
