"""The spec module's controller around fakes, with every service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.example_reader import FakeExampleReader
from tests.fakes.folders import FakeFolders
from tests.fakes.own_checks import FakeOwnChecks
from tests.fakes.profile_format import FakeProfileFormat
from tests.fakes.profile_output import FakeProfileOutput
from tests.fakes.runtime import FakeRuntime
from tests.fakes.settings import FakeSettings
from tests.modules.spec.languages import RUNTIME
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.application.services.publishing import PublishingService


def controller(files: FakeArchitectureFiles, settings: FakeSettings | None = None,
               output: FakeProfileOutput | None = None, folders: FakeFolders | None = None,
               runtime: FakeRuntime = RUNTIME, reader: FakeExampleReader | None = None,
               own: FakeOwnChecks | None = None) -> SpecController:
    settings = settings if settings is not None else FakeSettings()
    output = output if output is not None else FakeProfileOutput()
    architectures = ArchitectureService(files, runtime, reader if reader is not None else FakeExampleReader())
    folders = folders if folders is not None else FakeFolders()
    selection = ProfileSelectionService(settings, architectures, files, folders)
    return SpecController(architectures, selection, ProfileReviewService(selection, architectures, files,
                                                                          own if own is not None else FakeOwnChecks()),
                          ExplainService(files, architectures), MigrationService(files, architectures, output, FakeProfileFormat()),
                          ProfileCreationService(files, architectures, output, FakeProfileFormat()), PublishingService(architectures))
