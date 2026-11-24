"""Tests beside the code, wired: a scratch project whose profile says testing: {preset: pytest, beside: true} is
checked through the real reader. A test of a part sits beside its code, read as a test of the tier its part names and
never as code of its part; a test left below the tests folder is reported by test-tree; a tier's folder keeps its
tests below the tests folder. The same project without beside reads that file as app code."""
from pathlib import Path

from tests.bootstrap.project import app_check, write

PROFILE = """\
name: near
testing: TESTING
parts:
  domain:
    path: modules/<module>/domain
    role: the rules of a module
    tests: unit
  contract:
    path: modules/<module>/contract
    role: the results of the use cases
    imports: {may: [domain]}
    tests: unit
  application:
    path: modules/<module>/application
    role: the use cases
    imports: {may: [domain, contract]}
    holds: {classes: {names: "*Controller"}, functions: {names: "build_*"}}
    tests: unit
  scripts:
    path: scripts
    role: one-off scripts
    untested: run by hand
tiers:
  unit:
    proves: a rule
    litmus: Does it decide?
  guard:
    proves: the architecture
    litmus: Does it read the source?
    folder: architecture
fakes: {folder: fakes, for: [domain]}
excluded: {vendor: copied code}
guards:
  scenario-coverage: {results: contract, tier: unit, suffix: Result, columns: [given, when, then], file: "test_{name:snake}.py"}
  closed-tree: {}
"""
BESIDE = "{preset: pytest, beside: true}"
PUBLISH = '''"""Publish a document."""
from app.modules.docs.contract.results import Missing, Published, PublishResult


class PublishController:
    """Publishes a document when it exists."""

    def publish(self, found: bool) -> PublishResult:
        return Published() if found else Missing()
'''
TABLE = '''"""Use case: publish a document."""
import pytest

from app.modules.docs.application.publish import PublishController
from app.modules.docs.contract.results import Missing, Published


@pytest.mark.parametrize("given, when, then", [
    pytest.param(True, "publish", Published, id="a document that exists is published"),
    pytest.param(False, "publish", Missing, id="a document that does not exist is missing"),
])
def test_publish(given, when, then):
    assert isinstance(PublishController().publish(given), then)
'''
NEAR = "app/modules/docs/application/test_publish.py"
APP = {
    "__init__.py": "",
    "modules/__init__.py": "",
    "modules/docs/__init__.py": "",
    "modules/docs/domain/__init__.py": "",
    "modules/docs/domain/document.py": '"""A document."""\n\n\nclass Document:\n    """A document."""\n',
    "modules/docs/contract/__init__.py": "",
    "modules/docs/contract/results.py":
        '"""The results."""\n\n\nclass Published:\n    """Published."""\n\n\nclass Missing:\n    """Missing."""\n\n\n'
        "PublishResult = Published | Missing\n",
    "modules/docs/application/__init__.py": "",
    "modules/docs/application/publish.py": PUBLISH,
    "modules/docs/application/test_publish.py": TABLE,
    "scripts/__init__.py": "",
    "scripts/seed.py": '"""Seed the store."""\n\n\ndef run():\n    return 1\n',
    "vendor/test_copied.py": "def test_copied(:\n",
}
TESTS = {
    "conftest.py": "",
    "fakes/document.py": '"""A fake."""\n\n\nclass FakeDocument:\n    """A fake document."""\n',
    "architecture/test_rules.py": "from pathlib import Path\n\n\ndef test_rules():\n    assert Path\n",
}
STRAY = ("lies below the tests folder, but testing.beside keeps the tests of a part beside its code",
         "move it beside the code it tests")


def check(tmp_path: Path, testing: str = BESIDE, app: dict[str, str | None] | None = None,
          tests: dict[str, str | None] | None = None, with_tests: bool = True):
    """The violations of `xarch check` on the scratch project, its app and tests as given over APP and TESTS (None
    removes a file), its profile's testing as given, and its tests folder given to check unless with_tests is false."""
    app_files = {k: v for k, v in {**APP, **(app or {})}.items() if v is not None}
    test_files = {k: v for k, v in {**TESTS, **(tests or {})}.items() if v is not None}
    root = write(tmp_path / "app", app_files)
    folder = write(tmp_path / "tests", test_files)
    (tmp_path / "near.yaml").write_text(PROFILE.replace("TESTING", testing))
    return app_check(root, str(tmp_path / "near.yaml"), folder if with_tests else None).violations


def of(violations, file: str) -> list[tuple[str, str, str]]:
    return [(v.rule, v.message, v.fix) for v in violations if v.file == file]


def test_a_test_beside_the_code_is_a_test_and_no_code_of_its_part(tmp_path):
    found = check(tmp_path)
    assert of(found, NEAR) == []
    assert [v for v in found if v.rule == "scenario-coverage"] == []
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_beside_the_code_imports_only_what_its_part_may_and_is_named_by_its_app_path(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": "from app.scripts.seed import run\n" + TABLE})
    assert [(rule, message.split(":")[0]) for rule, message, _ in of(found, NEAR)] == [
        ("tiers", "a test of application/ (unit tier) may not import scripts/ (app.scripts.seed)")]


def test_the_guard_finds_the_table_test_beside_the_code_and_misses_it_when_it_is_gone(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": None})
    assert [(v.file, v.message) for v in found if v.rule == "scenario-coverage"] == [
        ("app/modules/docs/contract/results.py",
         "PublishResult has no test file test_publish.py among the unit tests of docs (scenario-coverage)")]


def test_a_test_left_below_the_tests_folder_is_reported_by_test_tree(tmp_path):
    found = check(tmp_path, tests={"modules/docs/application/test_publish.py": TABLE})
    assert [(v.file, v.line, v.message, v.fix) for v in found if v.rule == "test-tree"] == [
        ("tests/modules/docs/application/test_publish.py", 0, *STRAY)]


def test_a_test_in_a_tier_s_folder_stays_there_and_is_held_to_its_tier(tmp_path):
    assert of(check(tmp_path), "tests/architecture/test_rules.py") == []
    found = check(tmp_path, tests={"architecture/test_rules.py": "from app.modules.docs.domain.document import Document\n"})
    assert [(rule, message.startswith("a guard test may not import domain/"))
            for rule, message, _ in of(found, "tests/architecture/test_rules.py")] == [("tiers", True)]


def test_without_beside_the_same_file_is_code_of_its_part_and_the_mirrored_tree_is_not_reported(tmp_path):
    found = check(tmp_path, "pytest", tests={"modules/docs/application/test_publish.py": TABLE})
    assert "names" in [rule for rule, _, _ in of(found, NEAR)]
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_beside_the_code_of_an_untested_part_says_its_part_is_untested(tmp_path):
    found = check(tmp_path, app={"scripts/test_seed.py": "def test_seed():\n    assert True\n"})
    assert of(found, "app/scripts/test_seed.py") == [
        ("tiers", "lies in no tier: its part is untested", "test the part with a tier, or move the test")]


def test_a_test_beside_the_code_may_not_import_another(tmp_path):
    found = check(tmp_path, app={
        "modules/docs/application/test_other.py": "def test_other():\n    assert True\n",
        "modules/docs/application/test_publish.py":
            "from app.modules.docs.application.test_other import test_other\n" + TABLE})
    assert [message.split(":")[0] for rule, message, _ in of(found, NEAR) if rule == "tiers"] == [
        "a test may not import another test file (app.modules.docs.application.test_other)"]


def test_a_broken_test_beside_the_code_is_reported_once(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_broken.py": "def test_broken(:\n"})
    assert [rule for rule, _, _ in of(found, "app/modules/docs/application/test_broken.py")] == ["syntax"]


def test_without_a_tests_folder_the_tests_beside_the_code_are_still_checked(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": "from app.scripts.seed import run\n" + TABLE},
                  with_tests=False)
    assert [rule for rule, _, _ in of(found, NEAR)] == ["tiers"]
    assert [v for v in found if v.rule == "test-tree"] == []


def test_a_test_in_an_excluded_folder_is_not_read(tmp_path):
    assert [v for v in check(tmp_path) if v.file.startswith("app/vendor")] == []


def test_a_test_beside_the_code_importing_the_app_relatively_is_held_to_its_tier(tmp_path):
    found = check(tmp_path, app={"modules/docs/application/test_publish.py": "from ....scripts.seed import run\n" + TABLE})
    assert [(rule, message.split(":")[0]) for rule, message, _ in of(found, NEAR)] == [
        ("tiers", "a test of application/ (unit tier) may not import scripts/ (app.scripts.seed)")]
