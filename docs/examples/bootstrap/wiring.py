from __future__ import annotations

from dataclasses import dataclass

from app.modules.rules.adapters.fs_source_tree import FsSourceTree
from app.modules.rules.adapters.spec_profile import SpecProfile
from app.modules.rules.application.controller import RulesController
from app.modules.rules.application.services.app_check import AppCheckService
from app.modules.spec.adapters.fs_architecture_files import FsArchitectureFiles
from app.modules.spec.application.controller import SpecController
from app.modules.spec.application.services.architecture import ArchitectureService
from app.platform.filesystem import FileSystem


@dataclass(frozen=True)
class Controllers:
    rules: RulesController
    spec: SpecController


def build_controllers() -> Controllers:
    fs = FileSystem()
    spec = SpecController(ArchitectureService(FsArchitectureFiles(fs)))
    rules = RulesController(AppCheckService(SpecProfile(spec), FsSourceTree(fs)))
    return Controllers(rules, spec)
