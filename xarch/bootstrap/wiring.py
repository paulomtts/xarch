"""Binds every port to its adapter, builds the services and controllers, and wraps spec's controller for its consumers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton as LayoutSkeleton
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheck
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.adapters.spec_skeleton import SpecSkeleton as RulesSkeleton
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.application.services.import_check import ImportCheck
from xarch.modules.scaffold.adapters.fs_files import FsFiles
from xarch.modules.scaffold.adapters.spec_skeleton import SpecSkeleton as ScaffoldSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import Scaffolding
from xarch.modules.spec.adapters.fs_architecture_files import FsArchitectureFiles
from xarch.modules.spec.adapters.pyproject_settings import PyprojectSettings
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
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
    return SpecController(SkeletonService(PyprojectSettings(fs or FileSystem(), TomlReader())))


def build_architectures(fs: FileSystem | None = None) -> ArchitectureService:
    return ArchitectureService(FsArchitectureFiles(fs or FileSystem(), DataFileReader()))


def load_architecture(location: str | Path) -> Architecture:
    """The architecture bundled under a name (e.g. "web") or in a .yaml or .json file; raises InvalidArchitecture."""
    return build_architectures().load(location)


def build_rules(fs: FileSystem, spec: SpecController) -> RulesController:
    return RulesController(ImportCheck(FsSourceTree(fs), RulesSkeleton(spec)))


def build_layout(fs: FileSystem, spec: SpecController) -> LayoutController:
    return LayoutController(StructureCheck(FsDisk(fs), LayoutSkeleton(spec)))


def build_scaffold(fs: FileSystem, spec: SpecController) -> ScaffoldController:
    return ScaffoldController(Scaffolding(FsFiles(fs), ScaffoldSkeleton(spec)))


def build_controllers() -> Controllers:
    fs = FileSystem()
    spec = build_spec(fs)                           # one spec feeds rules, layout and scaffold: they cannot drift
    return Controllers(build_rules(fs, spec), build_layout(fs, spec), build_scaffold(fs, spec), spec)
