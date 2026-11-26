"""Sanctioned exceptions to the layout through the real app: a folder or file of the layout that is missing, or a
folder below the tests that mirrors no folder of the app, that an entry of `structure.accepted` names with a reason,
is no `structure` (or `test-tree`) finding and is named in the enforcement section instead; an entry that accepts
nothing is itself a finding, so the list can only shrink."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: sparse
testing: pytest
tiers:
  unit:
    proves: a rule
parts:
  modules/<module>/:
    domain/:
      role: the rules of one module
      tests: unit
      errors.py: {role: the errors of the module, tests: unit}
"""
ACCEPTED = """\
structure:
  accepted:
    - {path: modules/billing/domain/errors.py, why: billing raises the kernel's errors until it has its own}
    - {path: tests/modules/legacy/, why: the legacy tests move with the legacy module}
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("sparse.yaml").write_text(PROFILE + ACCEPTED)
    for path in ("app/__init__.py", "app/modules/__init__.py", "app/modules/docs/domain/errors.py",
                 "app/modules/billing/domain/rules.py", "tests/modules/legacy/helpers.py",
                 "tests/modules/docs/domain/test_errors.py"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("")


def check() -> tuple[list[str], dict]:
    result = runner.invoke(app, ["check", "--profile", "sparse.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return ([f"{v['file']}:{v['line'] or 0}: {v['message']} [{v['rule']}]" for v in document["violations"]],
            document["enforcement"])


def test_a_missing_file_and_an_unmirrored_folder_an_entry_names_are_no_findings_and_are_named():
    found, enforcement = check()
    assert found == []
    assert enforcement["accepted_findings"] == [
        {"rule": "structure", "file": "app/modules/billing", "line": 0, "key": "structure.accepted",
         "message": "missing domain/errors.py", "why": "billing raises the kernel's errors until it has its own"},
        {"rule": "test-tree", "file": "tests/modules/legacy", "line": 0, "key": "structure.accepted",
         "message": "mirrors no folder of the app (app/modules/legacy)",
         "why": "the legacy tests move with the legacy module"}]


def test_the_text_output_names_each_accepted_finding_with_its_reason():
    result = runner.invoke(app, ["check", "--profile", "sparse.yaml"])
    assert ("  accepted:    app/modules/billing: missing domain/errors.py, which structure.accepted accepts: billing "
            "raises the kernel's errors until it has its own") in result.stdout


def test_an_entry_whose_path_is_there_is_a_finding():
    Path("app/modules/billing/domain/errors.py").write_text("")
    Path("app/modules/legacy/domain").mkdir(parents=True)
    Path("app/modules/legacy/domain/errors.py").write_text("")
    found, _ = check()
    assert found == [
        "app/modules/billing/domain/errors.py:0: structure.accepted accepts modules/billing/domain/errors.py as a "
        "finding of structure, and structure finds none there (structure.accepted) [structure]",
        "tests/modules/legacy:0: structure.accepted accepts tests/modules/legacy as a finding of test-tree, and "
        "test-tree finds none there (structure.accepted) [test-tree]"]


def test_an_entry_written_with_the_app_folder_first_is_told_to_write_its_path_below_the_app():
    Path("sparse.yaml").write_text(PROFILE + ACCEPTED.replace("{path: modules/", "{path: app/modules/"))
    result = runner.invoke(app, ["check", "--profile", "sparse.yaml", "--format", "json"])
    assert [(v["file"], v["fix"]) for v in json.loads(result.stdout)["violations"]
            if "structure.accepted" in v["message"]] == [
        ("app/app/modules/billing/domain/errors.py", "write the path relative to the app: "
         "modules/billing/domain/errors.py, not app/modules/billing/domain/errors.py")]


def test_what_no_entry_names_is_still_a_finding():
    Path("sparse.yaml").write_text(PROFILE)
    found, enforcement = check()
    assert found == ["app/modules/billing:0: missing domain/errors.py [structure]",
                     "tests/modules/legacy:0: mirrors no folder of the app (app/modules/legacy) [test-tree]"]
    assert "accepted_findings" not in enforcement


def test_an_entry_with_no_reason_is_refused():
    Path("sparse.yaml").write_text(PROFILE + "structure:\n  accepted:\n    - {path: modules/billing/domain/errors.py}\n")
    result = runner.invoke(app, ["profile", "check", "sparse.yaml"])
    assert result.exit_code != 0 and "structure.accepted.0: missing `why`" in result.stdout
