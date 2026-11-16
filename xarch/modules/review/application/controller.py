from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.review.application.services.calibrating import CalibrationService
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.review.contract import (
    AllAndOthers,
    AllInPieces,
    Calibrate,
    CalibrateResult,
    KeyMissing,
    NothingChosen,
    Review,
    ReviewRefused,
    ReviewResult,
    TooManyFiles,
    UnknownEvals,
)
from xarch.modules.review.domain.errors import AllWithOthers, InPieces, NoKey, NoSelection, NoSuchEval, OverCap


class ReviewController:
    def __init__(self, reviewing: ReviewService, calibrating: CalibrationService):
        self._reviewing, self._calibrating = reviewing, calibrating

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
