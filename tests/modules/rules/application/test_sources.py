"""Use case: read the app's source files at the paths given, each with where the profile places it, on an in-memory
source tree: no filesystem."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON
from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.contract import (
    EXCLUDED,
    IN_NO_PART,
    IN_PART,
    IN_PROJECT,
    IN_TESTS,
    NOT_SOURCE,
    NOT_THERE,
    CheckRefused,
    ChecksCannotRun,
    Outside,
    ReadSources,
    SourceRead,
    SourcesRead,
)
from xarch.modules.rules.domain.values import PartInfo, Profile, SourceFile
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.placement import Repeat, Target

APP, TESTS, CWD = Path("/src/app"), Path("/src/tests"), Path("/src")
PROFILE = Profile(
    parts={"kernel": ("kernel",), "domain": ("modules", "*", "domain")},
    rules={"kernel": (), "domain": (Target("kernel"),)},
    folders=((), ("kernel",), ("modules",), ("modules", "*"), ("modules", "*", "domain")),
    repeats=(Repeat("module", ("modules",)),), excluded=(Excluded(("examples",), "shipped as data"),), language=PYTHON,
    info={"kernel": PartInfo("primitives", "Is it a primitive?", "kernel/"),
          "domain": PartInfo("invariants", "Is it an invariant?", "domain/")})
IDS = Import(1, ("app", "kernel", "ids"), ("Id",))
FILES = {"kernel/ids.py": [], "modules/docs/domain/values.py": [IDS], "stray/run.py": [], "examples/demo.py": [],
         "kernel/broken.py": SourceFile("", (), (), error=Unparsable(2, "invalid syntax"))}
TEXTS = {APP / "kernel/ids.py": "class Id: ...\n", APP / "modules/docs/domain/values.py": "from app.kernel.ids import Id\n",
         APP / "kernel/broken.py": "def (\n", Path("/src/README.md"): "# readme\n"}
VALUES = SourceRead("app/modules/docs/domain/values.py", IN_PART, "domain", "from app.kernel.ids import Id\n", (IDS,))
IDS_READ = SourceRead("app/kernel/ids.py", IN_PART, "kernel", "class Id: ...\n")
BROKEN = SourceRead("app/kernel/broken.py", IN_PART, "kernel", "def (\n", error=Unparsable(2, "invalid syntax"))
STRAY = SourceRead("app/stray/run.py", IN_NO_PART)


def sources(command):
    tree = FakeSourceTree(APP, FILES, {TESTS: {"test_ids.py": []}}, texts=TEXTS)
    profiles = FakeProfiles({"p": PROFILE}, refused={"broken": ("checks.mine.read: names no kind of fact",)},
                            unusable={"gone": "gone: cannot read the file: no such file"})
    return controller(tree, profiles).sources(command)


def read(*paths: str, profile: str = "p") -> ReadSources:
    return ReadSources(tuple(Path(p) for p in paths), CWD, APP, profile, TESTS)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FILES, read("app/modules/docs/domain/values.py"), SourcesRead((VALUES,)),
                 id="a file in a part is read with its part, its instance, its text and its imports"),
    pytest.param(FILES, read("/elsewhere/x.py"), Outside("/elsewhere/x.py lies outside the project: it is not below /src"),
                 id="a path outside the project is refused"),
    pytest.param(FILES, read("app/kernel/ids.py", profile="broken"),
                 ChecksCannotRun(("checks.mine.read: names no kind of fact",)),
                 id="a profile whose own checks cannot run is refused with every problem"),
    pytest.param(FILES, read("app/kernel/ids.py", profile="gone"), CheckRefused("gone: cannot read the file: no such file"),
                 id="a profile spec refuses is refused with spec's reason"),
])
def test_sources(given, when, then):
    assert sources(when) == then


@pytest.mark.parametrize("paths, files", [
    pytest.param(("app/kernel/broken.py",), (BROKEN,), id="a file that does not parse holds why"),
    pytest.param(("app/stray/run.py",), (STRAY,), id="a file in no part is not read"),
    pytest.param(("app/examples/demo.py",),
                 (SourceRead("app/examples/demo.py", EXCLUDED),),
                 id="a file below an excluded folder, named, is not read and says so"),
    pytest.param(("tests/test_ids.py",), (SourceRead("tests/test_ids.py", IN_TESTS),),
                 id="a test is not read"),
    pytest.param(("README.md",), (SourceRead("README.md", NOT_SOURCE),),
                 id="a file of another ending is no source file, wherever it lies"),
    pytest.param(("app/kernel/gone.py",), (SourceRead("app/kernel/gone.py", NOT_THERE),),
                 id="a path that is not there is not read"),
    pytest.param(("app",), (BROKEN, IDS_READ, VALUES, STRAY),
                 id="a folder stands for its source files but those below an excluded folder"),
    pytest.param(("app/kernel/ids.py", "app"), (IDS_READ, BROKEN, VALUES, STRAY),
                 id="a file found twice is read once, where it was first given"),
])
def test_each_file_found_is_placed_and_only_a_file_in_a_part_is_read(paths, files):
    assert sources(read(*paths)) == SourcesRead(files)


def test_a_source_file_of_the_project_outside_the_app_and_its_tests_lies_in_the_project():
    tree = FakeSourceTree(APP, {}, texts={Path("/src/scripts/run.py"): "x = 1\n"})
    assert controller(tree, FakeProfiles({"p": PROFILE})).sources(read("scripts/run.py")) == SourcesRead(
        (SourceRead("scripts/run.py", IN_PROJECT),))


def test_a_file_given_from_the_app_folder_is_found_as_from_the_project_root():
    assert sources(read("kernel/ids.py")) == SourcesRead((IDS_READ,))


def test_a_file_below_a_folder_the_profile_excludes_is_left_out_of_a_folder_only_when_the_profile_excludes_it():
    including = replace(PROFILE, excluded=())
    tree = FakeSourceTree(APP, {"examples/demo.py": []}, texts={})
    assert controller(tree, FakeProfiles({"p": including})).sources(read("app")) == SourcesRead(
        (SourceRead("app/examples/demo.py", IN_NO_PART),))
