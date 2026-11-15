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
                                               "application/logic", "application/ports", "adapters"]}
CONTROLLER = ROOT / "modules/docs/application/controller.py"


def run(disk: FakeDisk, package="app") -> list[str]:
    controller = LayoutController(StructureCheck(disk, SpecSkeleton(build_spec())))
    return [str(v) for v in controller.check(CheckStructure(ROOT, package, "cli")).violations]


def test_a_complete_tree_passes():
    assert run(FakeDisk(TOP | MODULE, {CONTROLLER})) == []


def test_violations_are_labelled_with_the_root_package():
    disk = FakeDisk((TOP - {ROOT / "kernel"}) | MODULE)
    assert run(disk, package="xarch") == ["xarch: missing kernel/", "xarch/modules/docs: missing application/controller.py"]


def test_folders_that_are_not_python_identifiers_are_not_modules():
    assert run(FakeDisk(TOP | {ROOT / "modules/_private", ROOT / "modules/not-a-module"})) == []


TESTS = Path("/src/tests")


def run_with_tests(disk: FakeDisk) -> list[str]:
    controller = LayoutController(StructureCheck(disk, SpecSkeleton(build_spec())))
    return [str(v) for v in controller.check(CheckStructure(ROOT, "app", "cli", TESTS)).violations]


def test_a_tests_tree_that_mirrors_the_app_passes():
    tests = {TESTS / p for p in ["", "modules", "modules/docs", "modules/docs/domain", "modules/docs/application",
                                 "modules/docs/__pycache__", "fakes", "anything"]}
    assert run_with_tests(FakeDisk(TOP | MODULE | {ROOT / "modules/docs/application"} | tests, {CONTROLLER})) == []


def test_a_folder_below_the_tests_of_the_each_folder_must_mirror_an_app_folder():
    tests = {TESTS / p for p in ["", "modules", "modules/docs", "modules/docs/domian", "modules/gone",
                                 "modules/gone/domain"]}
    assert run_with_tests(FakeDisk(TOP | MODULE | tests, {CONTROLLER})) == [
        "tests/modules/docs/domian: mirrors no folder of the app (app/modules/docs/domian)",
        "tests/modules/gone: mirrors no folder of the app (app/modules/gone)",
        "tests/modules/gone/domain: mirrors no folder of the app (app/modules/gone/domain)",
    ]
