"""The checks tied to a test framework (scenario-coverage, stand-ins and the tier mapping) take its names from the
profile: a profile that names another framework of the same shape gets the same checks, on files written in its
names, with messages and fixes in its names."""
from pathlib import Path

from tests.bootstrap.project import source_check

PROFILE = """
name: other
testing:
  files: ["*_spec.py"]
  functions: "it_*"
  tables: [{decorator: cases.table, columns_from: {position: 0}, rows: {position: 1}, row: cases.row,
            id: {keyword: name}}]
  mocks: {calls: [doubles.Double], spec_keywords: [of]}
parts:
  contract:   {path: modules/<module>/contract, role: results, tests: integration}
  controller:
    path: modules/<module>/application/controller.py
    role: maps
    imports:
      may: [contract, ports]
    tests: integration
  ports:      {path: modules/<module>/application/ports, role: ports, tests: integration}
tiers:
  integration: {proves: a use case, litmus: "Does it drive a controller?"}
fakes: {folder: fakes, for: [ports], prefix: Fake}
guards:
  scenario-coverage:
    results: contract
    tier: integration
    suffix: Result
    columns: [given, when, then]
    file: "{name:snake}_spec.py"
  stand-ins: {}
"""

APP = {
    "modules/docs/contract/__init__.py": "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "",
    "modules/docs/application/ports/notifier.py":
        "from typing import Protocol\n\nclass Notifier(Protocol):\n    def send(self) -> None: ...\n",
    "modules/docs/application/ports/repo.py":
        "from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self) -> str: ...\n",
}

ROWS = '''import cases
from app.modules.docs.contract import Missing, Published
{imports}
@cases.table("given, when, then", [
{rows}
])
def {name}(given, when, then):
    assert given == then
{more}'''

GOOD = ('    cases.row(1, 2, Published(), name="a document is published"),\n'
        '    cases.row(1, 2, Missing(), name="a document that is not there is missing"),')


def spec(rows: str = GOOD, name: str = "it_publishes", imports: str = "", more: str = "") -> str:
    return ROWS.format(rows=rows, name=name, imports=imports, more=more)


TESTS = {
    "modules/docs/application/publish_spec.py": spec(),
    "fakes/repo.py": "class FakeRepo: ...\n",
}


def check(tmp_path: Path, tests: dict[str, str], without: tuple[str, ...] = ()) -> list[str]:
    for root, files in (("app", APP), ("tests", {k: v for k, v in {**TESTS, **tests}.items() if k not in without})):
        for rel, body in files.items():
            (tmp_path / root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / root / rel).write_text(body)
    (tmp_path / "other.yaml").write_text(PROFILE)
    result = source_check(tmp_path / "app", str(tmp_path / "other.yaml"), tmp_path / "tests")
    return [f"{v}; fix: {v.fix}" for v in result.violations]


def test_a_table_written_in_the_names_of_the_profile_passes(tmp_path):
    assert check(tmp_path, {}) == []


def test_a_row_without_an_id_is_reported_in_the_names_of_the_profile(tmp_path):
    rows = GOOD + '\n    cases.row(1, 2, Missing()),'
    assert check(tmp_path, {"modules/docs/application/publish_spec.py": spec(rows)}) == [
        'tests/modules/docs/application/publish_spec.py:7: row has no id (scenario-coverage); fix: write '
        'cases.row(..., name="<a sentence stating the outcome>")']


def test_a_bare_row_is_reported_in_the_names_of_the_profile(tmp_path):
    rows = GOOD + "\n    (1, 2, Missing()),"
    assert check(tmp_path, {"modules/docs/application/publish_spec.py": spec(rows)}) == [
        'tests/modules/docs/application/publish_spec.py:7: row is not a cases.row(...) (scenario-coverage); fix: '
        'write cases.row(..., name="<a sentence stating the outcome>")']


def test_a_test_function_the_profile_does_not_name_is_not_a_table_test(tmp_path):
    assert check(tmp_path, {"modules/docs/application/publish_spec.py": spec(name="test_publishes")}) == [
        "tests/modules/docs/application/publish_spec.py:1: no table test whose parameters are given, when, then "
        "(scenario-coverage); fix: add a table test whose parameters are given, when, then"]


def test_a_use_case_whose_test_file_is_not_named_as_the_profile_says_is_reported_by_the_name_it_expects(tmp_path):
    tests = {"modules/docs/application/test_publish.py": spec()}
    assert check(tmp_path, tests, without=("modules/docs/application/publish_spec.py",)) == [
        "app/modules/docs/contract/__init__.py:4: PublishResult has no test file publish_spec.py among the "
        "integration tests of docs (scenario-coverage); fix: write publish_spec.py among the integration tests of "
        "docs"]


def test_a_mock_with_no_spec_is_reported_in_the_names_of_the_profile(tmp_path):
    more = "\n\ndef it_mocks():\n    Double()\n"
    found = check(tmp_path, {"modules/docs/application/publish_spec.py": spec(imports="from doubles import Double\n",
                                                                              more=more)})
    assert found == ["tests/modules/docs/application/publish_spec.py:14: Double() names nothing it stands in for "
                     "(stand-ins); fix: give it a spec, such as Double(of=<port>)"]


def test_a_mock_of_a_read_port_points_to_its_fake(tmp_path):
    more = "\n\ndef it_mocks():\n    Double(of=Repo)\n"
    imports = "from doubles import Double\nfrom app.modules.docs.application.ports.repo import Repo\n"
    found = check(tmp_path, {"modules/docs/application/publish_spec.py": spec(imports=imports, more=more)})
    assert found == ["tests/modules/docs/application/publish_spec.py:15: Double(of=Repo) stands in for Repo, a read "
                     "port (stand-ins); fix: use its fake FakeRepo"]


def test_a_mock_of_a_name_the_profile_does_not_list_is_not_checked(tmp_path):
    more = "\n\ndef it_mocks():\n    Mock()\n"
    assert check(tmp_path, {"modules/docs/application/publish_spec.py": spec(imports="from unittest.mock import Mock\n",
                                                                           more=more)}) == []


def test_a_file_the_profile_names_as_a_test_but_that_mirrors_no_part_has_no_tier(tmp_path):
    found = check(tmp_path, {"elsewhere/stray_spec.py": "", "elsewhere/test_stray.py": ""})
    assert found == ["tests/elsewhere/stray_spec.py: lies in no tier: no part's folder and no tier's `folder` is "
                     "mirrored here; fix: move it to the folder that mirrors its subject's path in the app, or into a "
                     "tier's `folder`"]


def test_a_profile_with_no_testing_key_names_no_framework_and_still_checks(tmp_path):
    (tmp_path / "app" / "sub").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "app" / "sub" / "a.py").write_text("x = 1\n")
    (tmp_path / "tests" / "test_a.py").write_text("import pytest\n")
    (tmp_path / "min.yaml").write_text('name: min\n'
                                       'parts: {sub: {path: sub, role: "the only part"}}\n')
    assert source_check(tmp_path / "app", str(tmp_path / "min.yaml"), tmp_path / "tests").violations == ()
