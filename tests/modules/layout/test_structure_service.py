"""Unit tests for the structure check on an in-memory disk."""
from pathlib import Path

from xarch.bootstrap.wiring import build_spec
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheck
from xarch.modules.layout.contract import CheckStructure
from tests.fakes.filesystem import FakeDisk

ROOT = Path("/src/pkg")
TOP = {ROOT / n for n in ["bootstrap", "kernel", "modules", "platform", "cli"]}
MODULE = {ROOT / "modules/docs" / p for p in ["", "contract", "domain", "application/services",
                                               "application/ports", "adapters"]}
CONTROLLER = ROOT / "modules/docs/application/controller.py"


def run(disk: FakeDisk, package="app") -> list[str]:
    controller = LayoutController(StructureCheck(disk, SpecSkeleton(build_spec())))
    return [str(v) for v in controller.check(CheckStructure(ROOT, package)).violations]


def test_a_complete_tree_passes():
    assert run(FakeDisk(TOP | MODULE, {CONTROLLER})) == []


def test_violations_are_labelled_with_the_root_package():
    disk = FakeDisk((TOP - {ROOT / "kernel"}) | MODULE)
    assert run(disk, package="xarch") == ["xarch: missing kernel/", "xarch/modules/docs: missing application/controller.py"]


def test_folders_that_are_not_python_identifiers_are_not_modules():
    assert run(FakeDisk(TOP | {ROOT / "modules/_private", ROOT / "modules/not-a-module"})) == []
