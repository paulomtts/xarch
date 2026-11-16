"""Binds every port to its adapter, builds the services and controllers, and wraps spec's controller for its consumers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton as LayoutSkeleton
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.adapters.layout_structure import LayoutStructure
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.application.controller import ReaderController, RulesController
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.scaffold.adapters.fs_files import FsFiles
from xarch.modules.scaffold.adapters.spec_skeleton import SpecSkeleton as ScaffoldSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.spec.adapters.fs_architecture_files import FsArchitectureFiles
from xarch.modules.spec.adapters.fs_folders import FsFolders
from xarch.modules.spec.adapters.fs_profile_output import FsProfileOutput
from xarch.modules.spec.adapters.interpreter_runtime import InterpreterRuntime
from xarch.modules.spec.adapters.pyproject_settings import PyprojectSettings
from xarch.modules.spec.adapters.yaml_profile_format import YamlProfileFormat
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.explanation import ExplainService
from xarch.modules.spec.application.services.migration import MigrationService
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.application.services.publishing import PublishingService
from xarch.modules.spec.domain.values import Architecture
from xarch.platform.data_files import DataFileReader
from xarch.platform.filesystem import FileSystem
from xarch.platform.package_data import PackageData
from xarch.platform.toml import TomlReader
from xarch.platform.yaml_writer import YamlWriter

BUNDLED = PackageData("xarch", "architectures")
"""Where the bundled profiles, their files and the testing presets ship."""

READER = FsSourceTree
"""The reader of the checked source, the one language xarch reads (its own docstring says which). It reads whatever the
profile's language names; a second language needs a reader of its own, chosen here by the language the profile names."""
RUNTIME = InterpreterRuntime
"""What that language says of itself (its standard library, reserved words and the names it binds before any code),
as the interpreter running xarch says it; a second language needs its own, chosen here with its reader."""


@dataclass(frozen=True)
class Controllers:
    rules: RulesController
    layout: LayoutController
    scaffold: ScaffoldController
    spec: SpecController


def build_reader(tree: FsSourceTree) -> ReaderController:
    """The reader of the app's language, which needs no profile: spec reads its examples with it, as its ExampleReader."""
    return ReaderController(SourceReadService(tree))


def build_spec(fs: FileSystem | None = None, tree: FsSourceTree | None = None) -> SpecController:
    """Spec, whose examples the reader reads: tree when one is given, else a reader of its own."""
    fs = fs or FileSystem()
    files = FsArchitectureFiles(fs, DataFileReader(), BUNDLED)
    architectures = ArchitectureService(files, RUNTIME(), build_reader(tree or READER(fs)))
    settings = PyprojectSettings(fs, TomlReader())
    output = FsProfileOutput(fs)
    folders = FsFolders(fs)
    selection = ProfileSelectionService(settings, architectures, files, folders)
    return SpecController(architectures, selection, ProfileReviewService(selection, architectures, files),
                          ExplainService(files, architectures),
                          MigrationService(files, architectures, output, YamlProfileFormat(YamlWriter())),
                          ProfileCreationService(files, architectures, output), PublishingService(architectures))


def build_architectures(fs: FileSystem | None = None) -> ArchitectureService:
    fs = fs or FileSystem()
    return ArchitectureService(FsArchitectureFiles(fs, DataFileReader(), BUNDLED), RUNTIME(), build_reader(READER(fs)))


def load_architecture(location: str | Path) -> Architecture:
    """The architecture bundled under a name (e.g. "web") or in a .yaml or .json file; raises InvalidArchitecture."""
    return build_architectures().load(location)


def build_rules(tree: FsSourceTree, spec: SpecController, layout: LayoutController) -> RulesController:
    profiles = SpecProfiles(spec)
    source = SourceCheckService(tree, profiles)
    return RulesController(source, LocateService(tree, profiles),
                           AppCheckService(source, LayoutStructure(layout), tree), ExplainingService(profiles),
                           ExamplesService(tree, profiles))


def build_layout(fs: FileSystem, spec: SpecController) -> LayoutController:
    return LayoutController(StructureCheckService(FsDisk(fs), LayoutSkeleton(spec)))


def build_scaffold(fs: FileSystem, spec: SpecController) -> ScaffoldController:
    return ScaffoldController(ScaffoldingService(FsFiles(fs), ScaffoldSkeleton(spec)))


def build_controllers() -> Controllers:
    """Built in the order each needs the one before: the reader, which needs no profile; spec, which reads its
    examples with it; layout and scaffold, which read the skeleton spec gives; rules, which reads with the same reader
    the profile spec gives and the structure layout checks. One reader and one spec feed them all: they cannot drift."""
    fs = FileSystem()
    tree = READER(fs)
    spec = build_spec(fs, tree)
    layout = build_layout(fs, spec)
    return Controllers(build_rules(tree, spec, layout), layout, build_scaffold(fs, spec), spec)
