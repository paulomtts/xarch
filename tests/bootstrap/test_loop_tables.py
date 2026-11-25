"""A framework whose table is the loop of a test's body over a list of the file's (`for given, when, then in CASES:`),
read for real by the Python reader: scenario-coverage checks its rows, and neither it nor plain_tables takes that loop
for a branch of the test."""
from pathlib import Path

from tests.bootstrap.project import line_of, source_check

PROFILE = """
name: looped
testing:
  files: ["test_*.py"]
  declared: [{function: "test_*"}]
  tables: [{loop: true, columns_from: bound, row: literal, id: {position: 0}}]
  mocks: {calls: [doubles.Double], specs: [{keyword: of}]}
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
  integration: {proves: a use case, litmus: "Does it drive a controller?", plain_tables: true}
fakes: {folder: fakes, for: [ports], prefix: Fake}
guards:
  scenario-coverage:
    results: contract
    tier: integration
    suffix: Result
    columns: [given, when, then]
    file: "test_{name:snake}.py"
  stand-ins: {}
"""

APP = {
    "modules/docs/contract/__init__.py": "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "",
    "modules/docs/application/ports/repo.py":
        "from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self) -> str: ...\n",
}

PUBLISHED = '    ("a document is published", 1, Published()),\n'
MISSING = '    ("a document that is not there is missing", 2, Missing()),\n'
BODY = "        assert given and when and then\n"

TEST = '''from app.modules.docs.contract import Missing, Published

CASES = {cases}


def test_publish():
    for given, when, then in CASES:
{body}{more}'''


def publish(cases: str = f"[\n{PUBLISHED}{MISSING}]", body: str = BODY, more: str = "") -> str:
    return TEST.format(cases=cases, body=body, more=more)


TESTED = "tests/modules/docs/application/test_publish.py"


def check(tmp_path: Path, test: str) -> list[str]:
    files = {"app": APP, "tests": {"modules/docs/application/test_publish.py": test, "fakes/repo.py": "class FakeRepo: ...\n"}}
    for root, written in files.items():
        for rel, body in written.items():
            (tmp_path / root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / root / rel).write_text(body)
    (tmp_path / "looped.yaml").write_text(PROFILE)
    result = source_check(tmp_path / "app", str(tmp_path / "looped.yaml"), tmp_path / "tests")
    return [f"{v}; fix: {v.fix}" for v in result.violations]


def test_a_loop_over_a_list_of_the_file_with_a_row_per_variant_covers_the_use_case_and_is_no_branch(tmp_path):
    assert check(tmp_path, publish()) == []


def test_a_variant_with_no_row_is_reported_at_the_loop(tmp_path):
    test = publish(cases=f"[\n{PUBLISHED}]")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'for given')}: PublishResult variant Missing has no row in the table and no "
        "standalone test naming it (scenario-coverage); fix: add a row whose then is Missing, or a standalone test "
        "naming it"]


def test_a_standalone_test_that_names_the_variant_and_runs_over_no_list_of_the_file_covers_it(tmp_path):
    more = "\n\ndef test_missing():\n    assert Missing()\n"
    assert check(tmp_path, publish(cases=f"[\n{PUBLISHED}]", more=more)) == []


def test_a_branch_inside_the_loop_is_reported_once_at_its_own_line_and_the_loop_is_not(tmp_path):
    test = publish(body="        if when:\n            pass\n" + BODY)
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'if when')}: test_publish has an `if` in its body (scenario-coverage); fix: arrange "
        "from given, act with when, assert == then, and give the odd case its own test"]


def test_a_loop_over_a_name_of_the_file_bound_to_no_list_is_reported_at_the_loop_as_rows_that_cannot_be_read(tmp_path):
    test = "from app.cases import load\n" + publish(cases="load()")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, 'for given')}: the rows of the table cannot be read (scenario-coverage); fix: write "
        "them as a list, or as the name of a list assigned at the top of the file"]


def test_a_row_that_is_not_a_literal_is_reported_in_the_words_of_the_form(tmp_path):
    test = publish(cases=f"[\n{PUBLISHED}{MISSING}    Published,\n]")
    assert check(tmp_path, test) == [
        f"{TESTED}:{line_of(test, '    Published,')}: row is not a literal (scenario-coverage); fix: write the row's "
        "id, a sentence stating the outcome, as its value at position 0"]
