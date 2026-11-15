"""The rules module's controller around fakes, with every service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.fakes.structure import FakeStructure
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService


def controller(tree: FakeSourceTree, profiles: FakeProfiles, structure: FakeStructure | None = None) -> RulesController:
    source = SourceCheckService(tree, profiles)
    return RulesController(source, LocateService(tree, profiles),
                           AppCheckService(source, structure if structure is not None else FakeStructure(), tree))
