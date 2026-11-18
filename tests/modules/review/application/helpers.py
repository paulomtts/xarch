"""The review module's controller around fakes, with its services, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.review import FakeAcceptances, FakeAnswers, FakeCalibrations, FakeCode, FakeDecisionModel, FakeProfile
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.application.services.accepting import AcceptingService
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.application.services.calibrating import CalibrationService
from xarch.modules.review.application.services.reviewing import ReviewService


def controller(code: FakeCode, profile: FakeProfile, model: FakeDecisionModel, answers: FakeAnswers,
               calibrations: FakeCalibrations | None = None,
               acceptances: FakeAcceptances | None = None) -> ReviewController:
    held = calibrations if calibrations is not None else FakeCalibrations()
    accepted = acceptances if acceptances is not None else FakeAcceptances()
    answering = AnsweringService(model, answers)
    reviewing = ReviewService(code, profile, model, answering, held, accepted)
    return ReviewController(reviewing, CalibrationService(code, profile, model, answering, held),
                            AcceptingService(reviewing, code, profile, accepted))
