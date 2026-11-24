"""A test-only framework that writes no table form, its tests methods of a class (`*Test.py` files, `Test*` names),
read for real by the Python reader: scenario-coverage asks every variant of a use case's union to be named by a test
of its file, weak when none of them asserts, and the profile is refused when it writes the guard's columns or a tier's
plain_tables."""
from pathlib import Path

import pytest

from tests.bootstrap.project import line_of, source_check
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.rules.contract import AppChecked, Weak
from xarch.modules.spec.domain.errors import InvalidArchitecture

PROFILE = """name: untabled
testing:
  files: ["*Test.py"]
  declared:
    - function: "Test*"
  tables: []
parts:
  contract:   {path: modules/<module>/contract, role: results, tests: integration}
  controller:
    path: modules/<module>/application/controller.py
    role: maps
    imports:
      may: [contract]
    tests: integration
tiers:
  integration:
    proves: a use case
    litmus: "Does it drive a controller?"
guards:
  scenario-coverage:
    results: contract
    tier: integration
    suffix: Result
    file: "{name:pascal}Test.py"
"""

APP = {
    "modules/docs/contract/__init__.py":
        "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "",
}

PUBLISHED = "    def TestPublished(self):\n        assert Published()\n"
MISSING = "    def TestMissing(self):\n        assert Missing()\n"
TESTED = "tests/modules/docs/application/PublishTest.py"


def publish(*methods: str) -> str:
    return "from app.modules.docs.contract import Missing, Published\n\n\nclass PublishTest:\n" + "\n".join(methods)


def checked(tmp_path: Path, test: str) -> AppChecked:
    files = {"app": APP, "tests": {"modules/docs/application/PublishTest.py": test}}
    for root, written in files.items():
        for rel, body in written.items():
            (tmp_path / root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / root / rel).write_text(body)
    (tmp_path / "untabled.yaml").write_text(PROFILE)
    return source_check(tmp_path / "app", str(tmp_path / "untabled.yaml"), tmp_path / "tests")


def check(tmp_path: Path, test: str) -> list[str]:
    return [f"{v}; fix: {v.fix}" for v in checked(tmp_path, test).violations]


def refused(tmp_path: Path, profile: str) -> tuple[Path, tuple[str, ...]]:
    path = tmp_path / "untabled.yaml"
    path.write_text(profile)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    return path, tuple(caught.value.problems)


def test_a_test_method_naming_each_variant_covers_the_use_case(tmp_path):
    assert check(tmp_path, publish(PUBLISHED, MISSING)) == []


def test_a_variant_no_test_names_is_reported_at_the_top_of_the_file_though_the_file_imports_it(tmp_path):
    assert check(tmp_path, publish(PUBLISHED)) == [
        f"{TESTED}:1: PublishResult variant Missing is named by no test (scenario-coverage); fix: write a test naming "
        "Missing"]


def test_a_variant_named_only_by_a_test_that_never_asserts_is_weak_and_no_violation(tmp_path):
    test = publish(PUBLISHED, "    def TestMissing(self):\n        Missing()\n")
    result = checked(tmp_path, test)
    assert [str(v) for v in result.violations] == []
    assert result.enforcement.weak == (
        Weak("scenario-coverage", TESTED, line_of(test, "def TestMissing"),
             "PublishResult variant Missing is credited to TestMissing by name only: no assert in their bodies"),)


def test_the_guard_s_columns_are_refused_under_a_framework_that_writes_no_table_form(tmp_path):
    path, problems = refused(tmp_path, PROFILE + "    columns: [given, when, then]\n")
    assert problems == (f"{path}: guards.scenario-coverage.columns: drop `columns`: the framework writes no table, so "
                        "each result is its own test",)


def test_plain_tables_is_refused_under_a_framework_that_writes_no_table_form(tmp_path):
    litmus = '    litmus: "Does it drive a controller?"\n'
    path, problems = refused(tmp_path, PROFILE.replace(litmus, litmus + "    plain_tables: true\n"))
    assert problems == (f"{path}: tiers.integration.plain_tables: needs a table form: the framework of `testing` "
                        "writes none in `testing.tables`",)
