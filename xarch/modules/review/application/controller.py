from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.review.application.services.accepting import AcceptingService
from xarch.modules.review.application.services.calibrating import CalibrationService
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.review.contract import (
    Accept,
    AcceptResult,
    AllAndOthers,
    AllInPieces,
    Calibrate,
    CalibrateResult,
    KeyMissing,
    NoReason,
    NotAnswered,
    NotDoubtful,
    NothingChosen,
    NotJudged,
    NotRecorded,
    Review,
    ReviewRefused,
    ReviewResult,
    TooManyFiles,
    UnknownEvals,
)
from xarch.modules.review.domain.errors import (
    AllWithOthers,
    InPieces,
    NoAnswerKept,
    NoKey,
    NoSelection,
    NoSuchEval,
    NoWhy,
    OverCap,
    Undoubted,
    Unjudged,
    Unrecorded,
)


class ReviewController:
    def __init__(self, reviewing: ReviewService, calibrating: CalibrationService, accepting: AcceptingService):
        self._reviewing, self._calibrating, self._accepting = reviewing, calibrating, accepting

    def review(self, cmd: Review) -> ReviewResult:
        """No file chosen, every file asked for with others or in pieces, more files than one run judges and a review that would
        send with no key set each come back as their own Result; files or a profile that cannot be read are refused
        with why. Nothing is sent before every refusal is known."""
        try:
            return self._reviewing.review(cmd)
        except NoSelection:
            return NothingChosen()
        except AllWithOthers:
            return AllAndOthers()
        except InPieces:
            return AllInPieces()
        except OverCap as e:
            return TooManyFiles(e.chosen, e.cap)
        except NoKey as e:
            return KeyMissing(e.variable)
        except DomainError as e:
            return ReviewRefused(e.reason)

    def calibrate(self, cmd: Calibrate) -> CalibrateResult:
        """Evals asked for that the profile does not write, and a calibration that would send with no key set, each
        come back as their own Result; a profile or examples that cannot be read are refused with why. Nothing is sent
        before every refusal is known."""
        try:
            return self._calibrating.calibrate(cmd)
        except NoSuchEval as e:
            return UnknownEvals(e.names, e.known)
        except NoKey as e:
            return KeyMissing(e.variable)
        except DomainError as e:
            return ReviewRefused(e.reason)

    def accept(self, cmd: Accept) -> AcceptResult:
        """No reason given, no file chosen, a file review does not judge, one whose answer is not kept, one that does
        not read as doubtful, one to take out that the record does not name, and more files than one run judges each
        come back as their own Result; files, a profile or a record that cannot be read are refused with why. Nothing is
        recorded before every refusal is known, and nothing is ever sent."""
        try:
            return self._accepting.accept(cmd)
        except NoWhy:
            return NoReason()
        except NoSelection:
            return NothingChosen()
        except Unjudged as e:
            return NotJudged(e.files)
        except NoAnswerKept as e:
            return NotAnswered(e.files)
        except Undoubted as e:
            return NotDoubtful(e.readings)
        except Unrecorded as e:
            return NotRecorded(e.files)
        except OverCap as e:
            return TooManyFiles(e.chosen, e.cap)
        except DomainError as e:
            return ReviewRefused(e.reason)
