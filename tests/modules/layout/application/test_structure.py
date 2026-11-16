"""Use case: the structure of an app checked against its profile, through the controller on an in-memory disk; a
profile spec refuses is refused."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeDisk
from tests.fakes.layout_skeleton import FakeSkeleton
from xarch.kernel.violations import Violation
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.layout.contract import CheckStructure, StructureChecked, StructureRefused

ROOT = Path("/src/pkg")
SKELETON = FakeSkeleton([("kernel",)], refused={"gone": "gone: cannot read the file: no such file"})


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FakeDisk({ROOT / "kernel"}), CheckStructure(ROOT, "app", "cli"), StructureChecked(()),
                 id="an app that holds its layout has no violation"),
    pytest.param(FakeDisk(), CheckStructure(ROOT, "app", "cli"),
                 StructureChecked((Violation("app", 0, "missing kernel/", "structure", "create app/kernel/"),)),
                 id="a folder of the layout that is missing is a violation"),
    pytest.param(FakeDisk(), CheckStructure(ROOT, "app", "gone"),
                 StructureRefused("gone: cannot read the file: no such file"),
                 id="a profile spec refuses is refused with spec's reason"),
])
def test_structure(given, when, then):
    assert LayoutController(StructureCheckService(given, SKELETON)).check(when) == then
