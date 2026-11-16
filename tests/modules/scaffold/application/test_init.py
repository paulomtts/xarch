"""Use case: init builds the top level of a profile below an app folder, on in-memory files; a profile spec refuses is
refused."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeFiles
from tests.fakes.scaffold_skeleton import FakeSkeleton
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.application.services.scaffolding import ScaffoldingService
from xarch.modules.scaffold.contract import InitProject, Refused, ReportView, Scaffolded

ROOT = Path("/src/app")
SKELETON = FakeSkeleton([(("kernel",), True)], refused={"gone": "gone: cannot read the file: no such file"})
BUILT = [ROOT / "__init__.py", ROOT / "kernel" / "__init__.py"]


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FakeFiles(), InitProject(ROOT, "cli", Path("/src")),
                 Scaffolded(ReportView(created=[*BUILT, Path("/src/pyproject.toml")])),
                 id="the top level is built and the profile recorded in a new pyproject.toml"),
    pytest.param(FakeFiles(set(BUILT), {Path("/src/pyproject.toml"): '[tool.xarch]\nprofile = "cli"\n'}),
                 InitProject(ROOT, "cli", Path("/src")), Scaffolded(ReportView(skipped=[*BUILT, Path("/src/pyproject.toml")])),
                 id="what is there already is left alone"),
    pytest.param(FakeFiles(), InitProject(ROOT, "gone", Path("/src")), Refused("gone: cannot read the file: no such file"),
                 id="a profile spec refuses is refused with spec's reason"),
])
def test_init(given, when, then):
    assert ScaffoldController(ScaffoldingService(given, SKELETON)).init(when) == then
