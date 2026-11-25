"""Use case: check that the layout of a profile exists below a root, and that the tests mirror the app, through the
controller on an in-memory disk."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeDisk
from tests.fakes.layout_skeleton import FakeSkeleton
from tests.modules.layout.builders import BESIDE, PYTHON_NAMING
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.application.services.structure_check import StructureCheckService
from xarch.modules.layout.contract import CheckStructure

ROOT = Path("/src/pkg")
TOP = {ROOT / n for n in ["bootstrap", "kernel", "kernel/logic", "modules", "platform", "cli", "cli/commands"]}
MODULE = {ROOT / "modules/docs" / p for p in ["", "contract", "domain", "application/services",
                                               "application/logic", "application/ports", "adapters"]}
CONTROLLER = ROOT / "modules/docs/application/controller.py"
SKELETON = FakeSkeleton([("bootstrap",), ("kernel",), ("kernel", "logic"), ("modules",), ("platform",), ("cli",),
                         ("cli", "commands")],
                        {("modules",): [(("contract",), True), (("domain",), True),
                                        (("application", "controller.py"), False), (("application", "services"), True),
                                        (("application", "logic"), True), (("application", "ports"), True),
                                        (("adapters",), True)]}, naming=PYTHON_NAMING)


def run(disk: FakeDisk, package="app") -> list[str]:
    controller = LayoutController(StructureCheckService(disk, SKELETON))
    return [str(v) for v in controller.check(CheckStructure(ROOT, package, "cli")).violations]


def test_a_complete_tree_passes():
    assert run(FakeDisk(TOP | MODULE, {CONTROLLER})) == []


MAIN = ROOT / "__main__.py"
WITH_MAIN = FakeSkeleton([("kernel",)], top_files=[("__main__.py",)])


def run_with_main(disk: FakeDisk) -> list[str]:
    return [str(v) for v in LayoutController(StructureCheckService(disk, WITH_MAIN)).check(
        CheckStructure(ROOT, "app", "cli")).violations]


@pytest.mark.parametrize("given, then", [
    pytest.param(FakeDisk({ROOT / "kernel"}, {MAIN}), [], id="the file is there"),
    pytest.param(FakeDisk({ROOT / "kernel"}), ["app: missing __main__.py"], id="the file is missing"),
    pytest.param(FakeDisk({ROOT / "kernel", MAIN}), ["app: missing __main__.py"], id="a folder in its place is no file"),
])
def test_a_file_declared_at_the_top_level_must_exist_as_a_file(given, then):
    assert run_with_main(given) == then


NESTED = FakeSkeleton([("web",), ("web", "routes"), ("web", "ui")], top_files=[("web", "app.py"), ("main.py",)])


def run_nested(disk: FakeDisk) -> list[str]:
    return [str(v) for v in LayoutController(StructureCheckService(disk, NESTED)).check(
        CheckStructure(ROOT, "app", "cli")).violations]


def test_a_folder_or_file_declared_at_any_depth_outside_the_each_folder_is_required():
    whole = FakeDisk({ROOT / "web", ROOT / "web/routes", ROOT / "web/ui"}, {ROOT / "web/app.py", ROOT / "main.py"})
    assert run_nested(whole) == []
    assert run_nested(FakeDisk({ROOT / "web", ROOT / "web/ui"}, {ROOT / "web/app.py", ROOT / "main.py"})) == [
        "app: missing web/routes/"]
    assert run_nested(FakeDisk({ROOT / "web", ROOT / "web/routes", ROOT / "web/ui"}, {ROOT / "main.py"})) == [
        "app: missing web/app.py"]


def test_a_folder_that_is_missing_with_what_the_layout_holds_in_it_reports_each():
    assert run_nested(FakeDisk(set(), set())) == [
        "app: missing web/", "app: missing web/routes/", "app: missing web/ui/", "app: missing web/app.py",
        "app: missing main.py"]


def test_violations_are_labelled_with_the_root_package():
    disk = FakeDisk((TOP - {ROOT / "kernel"}) | MODULE)
    assert run(disk, package="xarch") == ["xarch: missing kernel/", "xarch/modules/docs: missing application/controller.py"]


def test_folders_that_are_not_python_identifiers_are_not_modules():
    assert run(FakeDisk(TOP | {ROOT / "modules/_private", ROOT / "modules/not-a-module"})) == []


TESTS = Path("/src/tests")


def run_with_tests(disk: FakeDisk) -> list[str]:
    controller = LayoutController(StructureCheckService(disk, SKELETON))
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


def test_a_missing_folder_is_a_structure_violation_that_says_what_to_create():
    disk = FakeDisk((TOP - {ROOT / "kernel"}) | MODULE, {CONTROLLER})
    found = LayoutController(StructureCheckService(disk, SKELETON)).check(CheckStructure(ROOT, "app", "cli")).violations
    assert [(v.rule, v.fix) for v in found] == [("structure", "create app/kernel/")]


def test_a_test_folder_that_mirrors_nothing_is_a_test_tree_violation():
    tests = {TESTS / p for p in ["", "modules", "modules/gone"]}
    disk = FakeDisk(TOP | MODULE | tests, {CONTROLLER})
    found = LayoutController(StructureCheckService(disk, SKELETON)).check(CheckStructure(ROOT, "app", "cli", TESTS)).violations
    assert [(v.rule, v.fix) for v in found] == [
        ("test-tree", "create app/modules/gone/ in the app, or move what it holds to the folder that mirrors its "
                      "subject, or remove it")]


TWO = FakeSkeleton([("kernel",), ("modules",), ("plugins",)],
                   {("modules",): [(("domain",), True)], ("plugins",): [(("hooks",), True), (("manifest.py",), False)]})
TWO_APP = {ROOT / p for p in ["kernel", "modules", "modules/docs", "modules/docs/domain", "plugins", "plugins/seo",
                              "plugins/seo/hooks"]}
MANIFEST = ROOT / "plugins/seo/manifest.py"


def run_two(disk: FakeDisk, tests: Path | None = None) -> list[str]:
    return [str(v) for v in LayoutController(StructureCheckService(disk, TWO)).check(
        CheckStructure(ROOT, "app", "cli", tests)).violations]


def test_every_instance_of_every_repeating_folder_must_hold_what_its_folder_declares():
    assert run_two(FakeDisk(TWO_APP, {MANIFEST})) == []
    assert run_two(FakeDisk(TWO_APP - {ROOT / "plugins/seo/hooks", ROOT / "modules/docs/domain"})) == [
        "app/modules/docs: missing domain/", "app/plugins/seo: missing hooks/", "app/plugins/seo: missing manifest.py"]


def test_an_instance_of_one_repeating_folder_is_not_asked_for_what_another_declares():
    disk = FakeDisk(TWO_APP | {ROOT / "modules/other", ROOT / "modules/other/domain"}, {MANIFEST})
    assert run_two(disk) == []


def test_a_folder_below_the_tests_of_each_repeating_folder_must_mirror_an_app_folder():
    tests = {TESTS / p for p in ["", "modules", "modules/docs/domain", "modules/gone", "plugins", "plugins/seo/hooks",
                                 "plugins/seo/other", "plugins/ghost"]}
    assert run_two(FakeDisk(TWO_APP | tests, {MANIFEST}), TESTS) == [
        "tests/modules/gone: mirrors no folder of the app (app/modules/gone)",
        "tests/plugins/ghost: mirrors no folder of the app (app/plugins/ghost)",
        "tests/plugins/seo/other: mirrors no folder of the app (app/plugins/seo/other)"]


NEAR = FakeSkeleton([("bootstrap",), ("kernel",), ("kernel", "logic"), ("modules",), ("platform",), ("cli",),
                     ("cli", "commands")],
                    {("modules",): [(("contract",), True), (("domain",), True),
                                    (("application", "controller.py"), False), (("application", "services"), True),
                                    (("application", "logic"), True), (("application", "ports"), True),
                                    (("adapters",), True)]}, naming=PYTHON_NAMING,
                    beside=BESIDE)


def run_beside(disk: FakeDisk) -> list[str]:
    controller = LayoutController(StructureCheckService(disk, NEAR))
    return [f"{v}: {v.fix}" for v in controller.check(CheckStructure(ROOT, "app", "cli", TESTS)).violations]


def test_under_beside_a_test_below_the_tests_root_outside_its_kept_folders_is_reported():
    tests = {TESTS / p for p in ["", "modules", "modules/docs", "modules/docs/application", "architecture", "fakes",
                                 "modules/docs/__pycache__"]}
    files = {TESTS / p for p in ["modules/docs/application/test_publish.py", "architecture/test_rules.py",
                                 "fakes/repo.py", "fakes/test_fake.py", "conftest.py",
                                 "modules/docs/__pycache__/test_publish.py"]}
    assert run_beside(FakeDisk(TOP | MODULE | tests, {CONTROLLER} | files)) == [
        "tests/modules/docs/application/test_publish.py: lies below the tests folder, but testing.beside keeps the "
        "tests of a part beside its code: move it beside the code it tests"]


def test_under_beside_a_folder_that_mirrors_nothing_is_not_reported():
    tests = {TESTS / p for p in ["", "modules", "modules/ghost"]}
    assert run_beside(FakeDisk(TOP | MODULE | tests, {CONTROLLER})) == []


def test_under_beside_without_a_tests_root_nothing_below_it_is_read():
    found = LayoutController(StructureCheckService(FakeDisk(TOP | MODULE, {CONTROLLER}), NEAR)).check(
        CheckStructure(ROOT, "app", "cli")).violations
    assert found == ()


SPARSE = FakeSkeleton([("kernel",), ("api", "v1")], {("modules",): [(("domain",), True), (("hooks", "run.py"), False)]},
                      naming=PYTHON_NAMING, when={None: {("api", "v1"): ("api",)},
                                                  ("modules",): {("hooks", "run.py"): ("hooks",)}})
"""A layout with an optional folder api/ at the top level holding v1/, and an optional folder hooks/ in each module
holding run.py."""
DOCS = {ROOT / "modules", ROOT / "modules/docs", ROOT / "modules/docs/domain"}


@pytest.mark.parametrize("given, then", [
    pytest.param(FakeDisk({ROOT / "kernel", *DOCS}), [],
                 id="optional parts that are not there ask for nothing"),
    pytest.param(FakeDisk({ROOT / "kernel", ROOT / "api", *DOCS, ROOT / "modules/docs/hooks"}),
                 ["app: missing api/v1/", "app/modules/docs: missing hooks/run.py"],
                 id="optional parts that are there ask for what they hold"),
    pytest.param(FakeDisk({ROOT / "kernel", ROOT / "api", ROOT / "api/v1", *DOCS, ROOT / "modules/docs/hooks"},
                          {ROOT / "modules/docs/hooks/run.py"}), [],
                 id="optional parts that hold what they should are complete"),
])
def test_what_an_optional_part_holds_is_required_only_where_the_part_is_there(given, then):
    found = LayoutController(StructureCheckService(given, SPARSE)).check(CheckStructure(ROOT, "app", "cli"))
    assert [str(v) for v in found.violations] == then
