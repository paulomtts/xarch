"""What lies with what through the real app, on a tier-first project laid out as a conformance case is: each SQL store
that has fakes below tests/fakes/<store>/ needs a contract below tests/conformance/<store>/, a folder the layout names
beside the stores (sql/models/) being none; a store's transaction needs a contract file, one accepted with a reason.
A source with no counterpart is a `counterpart` finding at it with its fix, an accepted one is named in the enforcement
section instead, a counterpart whose `for` matches nothing fails `--strict`, and `check PATH` shows the findings at or
below the paths given."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: tierfirst
testing: pytest
tiers:
  conformance:
    proves: the fake and the sql adapter agree
    folder: conformance
parts:
  adapters/sql/:
    <store>/:
      name: store
      role: the sql adapter of one store
      tests: conformance
    models/:
      role: the tables
      untested: read through the stores
counterparts:
  sql-fakes-have-conformance:
    for: adapters/sql/<store>/
    when: [tests/fakes/<store>/]
    has: tests/conformance/<store>/
    fix: "add tests/conformance/{store}/ proving the fake and the sql adapter agree"
  transaction-has-contract:
    for: adapters/sql/<store>/transaction.py
    has: tests/conformance/<store>/test_*_transaction_contract.py
    accepted:
      - {path: adapters/sql/files/transaction.py, why: no memory-vs-sql contract yet}
"""
VACUOUS = """\
  repo-has-port:
    for: adapters/sql/<store>/<port>_repo.py
    has: ports/<port>_repo.py
"""
FILES = ("app/__init__.py", "app/adapters/__init__.py", "app/adapters/sql/__init__.py",
         "app/adapters/sql/models/__init__.py", "app/adapters/sql/cart/__init__.py",
         "app/adapters/sql/shop/__init__.py", "app/adapters/sql/shop/transaction.py",
         "app/adapters/sql/files/__init__.py", "app/adapters/sql/files/transaction.py",
         "tests/fakes/cart/fake.py", "tests/fakes/shop/fake.py", "tests/fakes/models/fake.py",
         "tests/conformance/shop/test_shop_transaction_contract.py")
MISSING = ("app/adapters/sql/cart:0: adapters/sql/cart/ has no tests/conformance/cart/, though it has "
           "tests/fakes/cart/ (counterparts.sql-fakes-have-conformance) [counterpart]")


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("tierfirst.yaml").write_text(PROFILE)
    for path in FILES:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("")


def check(*args: str) -> tuple[int, list[str], dict]:
    result = runner.invoke(app, ["check", "--profile", "tierfirst.yaml", "--format", "json", *args])
    document = json.loads(result.stdout)
    return (result.exit_code,
            [f"{v['file']}:{v['line'] or 0}: {v['message']} [{v['rule']}]" for v in document["violations"]],
            document["enforcement"])


def test_a_store_with_fakes_and_no_contract_is_a_finding_and_a_folder_named_beside_the_stores_is_none():
    code, found, _ = check()
    assert (code, found) == (1, [MISSING])


def test_the_finding_says_the_profile_s_fix_in_text():
    result = runner.invoke(app, ["check", "--profile", "tierfirst.yaml"])
    assert ("app/adapters/sql/cart: adapters/sql/cart/ has no tests/conformance/cart/, though it has tests/fakes/cart/ "
            "(counterparts.sql-fakes-have-conformance)\n"
            "    fix: add tests/conformance/cart/ proving the fake and the sql adapter agree") in result.stdout


def test_the_accepted_source_and_what_each_counterpart_read_are_named_in_the_enforcement_section():
    _, _, enforcement = check()
    assert enforcement["accepted_findings"] == [
        {"rule": "counterpart", "file": "app/adapters/sql/files/transaction.py", "line": 0,
         "key": "counterparts.transaction-has-contract.accepted",
         "message": "adapters/sql/files/transaction.py has no tests/conformance/files/test_*_transaction_contract.py "
                    "(counterparts.transaction-has-contract)", "why": "no memory-vs-sql contract yet"}]
    assert [(item["id"], item["read"]) for item in enforcement["counterparts"]] == [
        ("sql-fakes-have-conformance", 3), ("transaction-has-contract", 2)]


def test_a_contract_added_clears_the_finding_and_an_accepted_source_that_now_has_one_is_a_finding():
    for path in ("tests/conformance/cart/test_cart.py", "tests/conformance/files/test_files_transaction_contract.py"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("")
    _, found, _ = check()
    assert found == [
        "app/adapters/sql/files/transaction.py:0: counterparts.transaction-has-contract.accepted names "
        "adapters/sql/files/transaction.py, which now has its counterpart "
        "tests/conformance/files/test_*_transaction_contract.py [counterpart]"]


def test_a_counterpart_whose_for_matches_nothing_reads_nothing_and_fails_strict():
    Path("tierfirst.yaml").write_text(PROFILE + VACUOUS)
    Path("tests/conformance/cart").mkdir(parents=True)
    Path("tests/conformance/cart/test_cart.py").write_text("")
    said = ("counterparts.repo-has-port matches nothing in the project, so it passes for want of anything to check: "
            "widen its for, or drop it")
    code, found, enforcement = check("--strict")
    assert (code, found) == (1, [])
    assert {"key": "vacuous", "detail": said} in enforcement["strict_failures"]
    text = runner.invoke(app, ["check", "--profile", "tierfirst.yaml"]).stdout
    assert f"  reads nothing: {said}" in text


def test_a_check_of_some_paths_shows_the_findings_at_or_below_them_alone():
    assert check("app/adapters/sql/shop")[1] == []
    assert check("app/adapters/sql/cart")[1] == [MISSING]


def test_a_placeholder_has_names_that_for_does_not_bind_is_refused_when_the_profile_loads():
    Path("tierfirst.yaml").write_text(PROFILE.replace("has: tests/conformance/<store>/\n",
                                                      "has: tests/conformance/<module>/\n"))
    result = runner.invoke(app, ["profile", "check", "tierfirst.yaml"])
    assert result.exit_code != 0
    assert "counterparts.sql-fakes-have-conformance.has: <module> is bound by no step of for" in result.stdout
