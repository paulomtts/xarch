"""Binds every port to its adapter, builds the services and controllers, and hands spec's controller to the adapters of
the modules that wrap it."""
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from xarch.modules.layout.adapters.fs_disk import FsDisk
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton as LayoutSkeleton
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.review.adapters.fs_acceptances import FsAcceptances
from xarch.modules.review.adapters.fs_answers import FsAnswers
from xarch.modules.review.adapters.fs_calibrations import FsCalibrations
from xarch.modules.review.adapters.rules_code import RulesCode
from xarch.modules.review.adapters.spec_profile import SpecWords
from xarch.modules.review.adapters.typesafe_model import KEY, TypeSafeModel
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.application.services.accepting import AcceptingService
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.application.services.calibrating import CalibrationService
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.adapters.layout_structure import LayoutStructure
from xarch.modules.rules.adapters.spec_check_format import SpecCheckFormat
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.application.controller import ReaderController, RulesController
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.asking import AskingService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.holding import HoldingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.application.services.sources import SourcesService
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
from xarch.modules.spec.application.services.profile_creation import ProfileCreationService
from xarch.modules.spec.application.services.profile_review import ProfileReviewService
from xarch.modules.spec.application.services.profile_selection import ProfileSelectionService
from xarch.modules.spec.application.services.publishing import PublishingService
from xarch.modules.spec.domain.values import Architecture
from xarch.platform.data_files import DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem
from xarch.platform.package_data import PackageData
from xarch.platform.toml import TomlReader
from xarch.platform.typesafe import URL, TypeSafe
from xarch.platform.yaml_writer import YamlWriter

BUNDLED = PackageData("xarch", "architectures")
"""Where the bundled profiles, their files and the testing presets ship."""

READER = FsSourceTree
"""The reader of the checked source, the one language xarch reads today (its own docstring says which), built once
when the app starts, before any command chooses a profile. A second language needs a reader of its own, and the
checks of rules and spec's example reading would then take a reader per language, built here, and pick one by the
language the profile names."""
RUNTIME = InterpreterRuntime
"""What that language says of itself (its standard library, reserved words and the names it binds before any code),
as the interpreter running xarch says it, for a language whose data file gives `standard: interpreter`; a language
whose data file lists them is not asked, and needs no runtime of its own."""
CODE = Path(__file__).parents[1]
"""xarch's own code, whose source the reader's cache is keyed by, so that a change of xarch reads every file afresh."""
CACHE = "XARCH_CACHE_DIR"
"""The environment variable naming the folder the reader keeps what it read in; set empty, it keeps nothing. Unset, the
folder is `xarch/` in the user's cache folder ($XDG_CACHE_HOME, else ~/.cache)."""
MODEL = "jev-1.14.0"
"""The version of the decision model review asks, pinned: the one the evidence for its lines was measured with. Each
answer kept records the version that gave it."""


@dataclass(frozen=True)
class _Controllers:
    rules: RulesController
    layout: LayoutController
    scaffold: ScaffoldController
    spec: SpecController
    review: ReviewController


def _build_reader(tree: FsSourceTree) -> ReaderController:
    """The reader of the app's language, which needs no profile: spec reads its examples with it, as its ExampleReader."""
    return ReaderController(SourceReadService(tree))


def _build_spec(fs: FileSystem, tree: FsSourceTree) -> SpecController:
    """Spec, whose examples the reader of tree reads."""
    files = FsArchitectureFiles(fs, DataFileReader(), BUNDLED)
    architectures = ArchitectureService(files, RUNTIME(), _build_reader(tree))
    settings = PyprojectSettings(fs, TomlReader())
    output = FsProfileOutput(fs)
    folders = FsFolders(fs)
    form = YamlProfileFormat(YamlWriter())
    selection = ProfileSelectionService(settings, architectures, files, folders)
    return SpecController(architectures, selection, ProfileReviewService(selection, architectures, files),
                          ExplainService(files, architectures), ProfileCreationService(files, architectures, output, form),
                          PublishingService(architectures, form))


def _build_architectures(fs: FileSystem | None = None) -> ArchitectureService:
    fs = fs or FileSystem()
    return ArchitectureService(FsArchitectureFiles(fs, DataFileReader(), BUNDLED), RUNTIME(), _build_reader(READER(fs)))


def load_architecture(location: str | Path) -> Architecture:
    """The architecture bundled under a name (e.g. "web") or in a .yaml or .json file; raises InvalidArchitecture."""
    return _build_architectures().load(location)


def _build_rules(tree: FsSourceTree, spec: SpecController, layout: LayoutController) -> RulesController:
    profiles = SpecProfiles(spec)
    source = SourceCheckService(tree, profiles)
    explaining = ExplainingService(profiles, SpecCheckFormat(spec))
    return RulesController(LocateService(tree, profiles), AppCheckService(source, LayoutStructure(layout), tree),
                           explaining, ExamplesService(tree, profiles), SourcesService(tree, profiles),
                           AskingService(tree, profiles), HoldingService(tree, profiles))


def _build_layout(fs: FileSystem, spec: SpecController) -> LayoutController:
    return LayoutController(StructureCheckService(FsDisk(fs), LayoutSkeleton(spec)))


def _build_scaffold(fs: FileSystem, spec: SpecController) -> ScaffoldController:
    return ScaffoldController(ScaffoldingService(FsFiles(fs), ScaffoldSkeleton(spec)))


def _cache(environment: Mapping[str, str]) -> Path | None:
    """The folder the reader keeps what it read in, as the environment says it (see CACHE); None keeps nothing, and so
    does an environment that names no home."""
    if CACHE in environment:
        return Path(environment[CACHE]) if environment[CACHE].strip() else None
    base = environment.get("XDG_CACHE_HOME", "")
    if not Path(base).is_absolute():
        home = environment.get("HOME", "")
        base = str(Path(home) / ".cache") if home and Path(home).is_absolute() else ""
    return Path(base) / "xarch" if base else None


def _client(environment: Mapping[str, str], url: str) -> TypeSafe | None:
    """The decision model's client, with the key the environment holds when it is asked, or None when it holds none:
    the key is read here alone, at the moment review would send, and handed to the client, nowhere else; it is read
    without the whitespace around it, and one of whitespace alone is none."""
    key = environment.get(KEY, "").strip()
    return TypeSafe(key, base_url=url, model=MODEL) if key else None


def _build_review(fs: FileSystem, rules: RulesController, spec: SpecController, environment: Mapping[str, str],
                  url: str) -> ReviewController:
    """Review, which reads the app's files through rules and the profile's words through spec, asks the decision model
    at url, its key read from environment, and keeps the answers, the record of the evals held to their examples and
    the record of the files accepted on the filesystem; accepting reads through the same review."""
    model = TypeSafeModel(partial(_client, environment, url), MODEL, url, DataFileWriter())
    answers = FsAnswers(fs, DataFileReader(), DataFileWriter())
    calibrations = FsCalibrations(fs, DataFileReader(), DataFileWriter())
    acceptances = FsAcceptances(fs, DataFileReader(), DataFileWriter())
    code, words, answering = RulesCode(rules), SpecWords(spec), AnsweringService(model, answers)
    reviewing = ReviewService(code, words, model, answering, calibrations, acceptances)
    return ReviewController(reviewing, CalibrationService(code, words, model, answering, calibrations),
                            AcceptingService(reviewing, code, words, acceptances))


def build_controllers(environment: Mapping[str, str] | None = None, url: str = URL) -> _Controllers:
    """Built in the order each needs the one before: the reader, which needs no profile; spec, which reads its
    examples with it; layout and scaffold, which read the skeleton spec gives; rules, which reads with the same reader
    the profile spec gives and the structure layout checks; review, which reads the app's files through rules and the
    profile's words through spec. One reader and one spec feed them all: they cannot drift. Review's key is read from
    environment (None: the process's own) when a question would be sent to the decision model at url; the reader's cache
folder is read from it when the controllers are built."""
    environment = os.environ if environment is None else environment
    fs = FileSystem()
    tree = READER(fs, _cache(environment), CODE)
    spec = _build_spec(fs, tree)
    layout = _build_layout(fs, spec)
    rules = _build_rules(tree, spec, layout)
    review = _build_review(fs, rules, spec, environment, url)
    return _Controllers(rules, layout, _build_scaffold(fs, spec), spec, review)
