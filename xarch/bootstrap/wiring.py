"""Binds every port to its adapter, builds the services and controllers, and wraps spec's controller for its consumers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton as LayoutSkeleton
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.scaffold.adapters.fs_files import FsFiles
from xarch.modules.scaffold.adapters.spec_skeleton import SpecSkeleton as ScaffoldSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.spec.adapters.fs_architecture_files import FsArchitectureFiles
from xarch.modules.spec.adapters.fs_profile_output import FsProfileOutput
from xarch.modules.spec.adapters.pyproject_settings import PyprojectSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.domain.values import Architecture
from xarch.platform.data_files import DataFileReader
from xarch.platform.filesystem import FileSystem
from xarch.platform.toml import TomlReader


@dataclass(frozen=True)
class Controllers:
    rules: RulesController
    layout: LayoutController
    scaffold: ScaffoldController
    spec: SpecController


def build_spec(fs: FileSystem | None = None) -> SpecController:
    fs = fs or FileSystem()
    files = FsArchitectureFiles(fs, DataFileReader())
    architectures = ArchitectureService(files)
    settings = PyprojectSettings(fs, TomlReader())
    output = FsProfileOutput(fs)
    selection = ProfileSelectionService(settings, architectures, files)
    return SpecController(architectures, selection, settings, ProfileReviewService(selection, architectures, files),
                          ExplainService(files), MigrationService(files, architectures, output),
                          ProfileCreationService(files, architectures, output))


def build_architectures(fs: FileSystem | None = None) -> ArchitectureService:
    return ArchitectureService(FsArchitectureFiles(fs or FileSystem(), DataFileReader()))


def load_architecture(location: str | Path) -> Architecture:
    """The architecture bundled under a name (e.g. "web") or in a .yaml or .json file; raises InvalidArchitecture."""
    return build_architectures().load(location)


def build_rules(fs: FileSystem, spec: SpecController) -> RulesController:
    tree, profiles = FsSourceTree(fs), SpecProfiles(spec)
    return RulesController(SourceCheckService(tree, profiles), LocateService(tree, profiles))


def build_layout(fs: FileSystem, spec: SpecController) -> LayoutController:
    return LayoutController(StructureCheckService(FsDisk(fs), LayoutSkeleton(spec)))


def build_scaffold(fs: FileSystem, spec: SpecController) -> ScaffoldController:
    return ScaffoldController(ScaffoldingService(FsFiles(fs), ScaffoldSkeleton(spec)))


def build_controllers() -> Controllers:
    """One spec feeds rules, layout and scaffold: they cannot drift."""
    fs = FileSystem()
    spec = build_spec(fs)
    return Controllers(build_rules(fs, spec), build_layout(fs, spec), build_scaffold(fs, spec), spec)
