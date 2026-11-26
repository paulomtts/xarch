"""Sanctioned exceptions to a check of the profile's own through the real app: a finding an entry of
`checks.<id>.accepted` names (by its file, and by the values of the variables the entry writes), with a reason, is no
finding and is named in the enforcement section instead; an entry that accepts nothing is itself a finding of the
check, so the list can only shrink."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

CHECK = """\
name: ratchet
testing: pytest
tiers:
  unit:
    proves: a rule
parts:
  core/:
    role: the core
    tests: unit
checks:
  no-local-clock:
    read: class
    in: {files: tests}
    may_not: {name: ["*Clock"]}
    message: "{file} defines its own clock {name}"
    fix: "use the shared FixedClock"
    examples:
      flagged: {tests/core/test_x.py: "class XClock: ...\\n"}
      clean: {tests/core/test_x.py: "class X: ...\\n"}
"""
ACCEPTED = """\
    accepted:
      - {file: tests/core/test_a.py, name: AClock, why: the a tests freeze two clocks}
      - {file: tests/core/test_b.py, why: the b suite is retired with b}
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    profile(ACCEPTED)
    for path, text in {
        "app/__init__.py": "", "app/core/__init__.py": "", "app/core/x.py": "X = 1\n",
        "tests/core/test_a.py": "class AClock: ...\nclass OtherClock: ...\n",
        "tests/core/test_b.py": "class BClock: ...\nclass B2Clock: ...\n",
    }.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)


def profile(accepted: str) -> None:
    Path("ratchet.yaml").write_text(CHECK.replace("    examples:\n", f"{accepted}    examples:\n"))


def check() -> tuple[list[str], dict]:
    result = runner.invoke(app, ["check", "--profile", "ratchet.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return [f"{v['file']}:{v['line'] or 0}: {v['message']}" for v in document["violations"]], document["enforcement"]


def test_a_finding_an_entry_accepts_is_no_violation_and_is_named_in_the_enforcement_section():
    found, enforcement = check()
    assert found == ["tests/core/test_a.py:2: tests/core/test_a.py defines its own clock OtherClock"]
    assert enforcement["accepted_findings"] == [
        {"rule": "no-local-clock", "file": "tests/core/test_a.py", "line": 1, "key": "checks.no-local-clock.accepted",
         "message": "tests/core/test_a.py defines its own clock AClock", "why": "the a tests freeze two clocks"},
        {"rule": "no-local-clock", "file": "tests/core/test_b.py", "line": 1, "key": "checks.no-local-clock.accepted",
         "message": "tests/core/test_b.py defines its own clock BClock", "why": "the b suite is retired with b"},
        {"rule": "no-local-clock", "file": "tests/core/test_b.py", "line": 2, "key": "checks.no-local-clock.accepted",
         "message": "tests/core/test_b.py defines its own clock B2Clock", "why": "the b suite is retired with b"}]


def test_the_text_output_names_each_accepted_finding_with_its_reason():
    result = runner.invoke(app, ["check", "--profile", "ratchet.yaml"])
    assert ("  accepted:    tests/core/test_a.py:1: tests/core/test_a.py defines its own clock AClock, which "
            "checks.no-local-clock.accepted accepts: the a tests freeze two clocks") in result.stdout


def test_an_entry_that_accepts_nothing_is_a_finding_of_the_check():
    Path("tests/core/test_a.py").write_text("class Other: ...\n")
    found, enforcement = check()
    assert found == ["tests/core/test_a.py:0: checks.no-local-clock.accepted accepts a finding of tests/core/test_a.py "
                     "with name AClock, and the check finds none (checks.no-local-clock.accepted)"]
    assert [item["file"] for item in enforcement["accepted_findings"]] == ["tests/core/test_b.py"] * 2


def test_an_entry_whose_file_is_gone_is_a_finding_of_the_check():
    Path("tests/core/test_b.py").unlink()
    found, _ = check()
    assert found == ["tests/core/test_a.py:2: tests/core/test_a.py defines its own clock OtherClock",
                     "tests/core/test_b.py:0: checks.no-local-clock.accepted accepts the findings of "
                     "tests/core/test_b.py, and the check finds none (checks.no-local-clock.accepted)"]


def test_a_check_accepting_nothing_has_no_accepted_findings_in_its_enforcement():
    profile("")
    found, enforcement = check()
    assert len(found) == 4 and "accepted_findings" not in enforcement


@pytest.mark.parametrize("entry, problem", [
    pytest.param("{file: tests/core/test_a.py, name: AClock}", "checks.no-local-clock.accepted.0: missing `why`",
                 id="no reason"),
    pytest.param("{name: AClock, why: x}", "checks.no-local-clock.accepted.0: missing `file`", id="no file"),
    pytest.param("{file: tests/core/test_a.py, line: 1, why: x}",
                 "checks.no-local-clock.accepted.0.line: a line moves with every edit above it: name the finding by "
                 "the value of a variable, such as name: <its name>, or accept every finding of the file",
                 id="a line"),
    pytest.param("{file: tests/core/test_a.py, nme: AClock, why: x}",
                 "checks.no-local-clock.accepted: no variable is named 'nme'", id="no variable"),
])
def test_an_entry_written_wrong_is_refused_with_its_problem(entry, problem):
    profile(f"    accepted:\n      - {entry}\n")
    result = runner.invoke(app, ["profile", "check", "ratchet.yaml"])
    assert result.exit_code != 0 and problem in result.stdout
