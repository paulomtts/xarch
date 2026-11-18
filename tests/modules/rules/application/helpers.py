"""The rules module's controller around fakes, with every service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.check_format import FakeCheckFormat
from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.fakes.structure import FakeStructure
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.asking import AskingService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.holding import HoldingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.sources import SourcesService


def controller(tree: FakeSourceTree, profiles: FakeProfiles, structure: FakeStructure | None = None) -> RulesController:
    source = SourceCheckService(tree, profiles)
    return RulesController(LocateService(tree, profiles),
                           AppCheckService(source, structure if structure is not None else FakeStructure(), tree),
                           ExplainingService(profiles, FakeCheckFormat()), ExamplesService(tree, profiles),
                           SourcesService(tree, profiles), AskingService(tree, profiles),
                           HoldingService(tree, profiles))
