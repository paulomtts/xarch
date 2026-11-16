"""The review module's controller around fakes, with its services, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.review import FakeAnswers, FakeCalibrations, FakeCode, FakeDecisionModel, FakeProfile
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.application.services.calibrating import CalibrationService
from xarch.modules.review.application.services.reviewing import ReviewService


def controller(code: FakeCode, profile: FakeProfile, model: FakeDecisionModel, answers: FakeAnswers,
               calibrations: FakeCalibrations | None = None) -> ReviewController:
    held = calibrations if calibrations is not None else FakeCalibrations()
    answering = AnsweringService(model, answers)
    return ReviewController(ReviewService(code, profile, model, answering, held),
                            CalibrationService(code, profile, model, answering, held))
