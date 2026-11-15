"""The spec module's controller around fakes, with every service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.folders import FakeFolders
from tests.fakes.profile_output import FakeProfileOutput
from tests.fakes.settings import FakeSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService


def controller(files: FakeArchitectureFiles, settings: FakeSettings | None = None,
               output: FakeProfileOutput | None = None, folders: FakeFolders | None = None) -> SpecController:
    settings = settings if settings is not None else FakeSettings()
    output = output if output is not None else FakeProfileOutput()
    architectures = ArchitectureService(files)
    selection = ProfileSelectionService(settings, architectures, files,
                                        folders if folders is not None else FakeFolders())
    return SpecController(architectures, selection, ProfileReviewService(selection, architectures, files),
                          ExplainService(files), MigrationService(files, architectures, output),
                          ProfileCreationService(files, architectures, output))
