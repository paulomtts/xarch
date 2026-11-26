"""Sanctioned exceptions to the tiers through the real app: a tiers finding an entry of `tiers.<tier>.accepted` names
(a test file of the tier or of no tier, and, if the entry says so, what it imports), with a reason, is no finding and
is named in the enforcement section instead; an entry that accepts nothing is itself a tiers finding, so the list can
only shrink."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: tiered
testing: pytest
tiers:
  unit:
    proves: a rule
ACCEPTED
parts:
  core/:
    role: the rules
    tests: unit
  store/:
    role: the store
    untested: the store is checked by hand
"""
ACCEPTED = """\
    accepted:
      - {file: tests/core/test_rates.py, import: store/db.py, why: the rates read the table until the port lands}
      - {file: tests/old/test_page.py, why: the old page tests are retired with the old page}
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    profile(ACCEPTED)
    for path, text in {
        "app/__init__.py": "", "app/core/__init__.py": "", "app/core/rates.py": "R = 1\n",
        "app/store/__init__.py": "", "app/store/db.py": "D = 1\n", "app/store/io.py": "I = 1\n",
        "tests/core/test_rates.py": "from app.store import db\nfrom app.store import io\n",
        "tests/old/test_page.py": "",
    }.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)


def profile(accepted: str) -> None:
    Path("tiered.yaml").write_text(PROFILE.replace("ACCEPTED\n", accepted))


def check() -> tuple[list[str], dict]:
    result = runner.invoke(app, ["check", "--profile", "tiered.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return ([f"{v['file']}:{v['line'] or 0}: {v['message']} [{v['rule']}]" for v in document["violations"]],
            document["enforcement"])


def test_an_import_and_a_file_in_no_tier_an_entry_names_are_no_findings_and_are_named():
    found, enforcement = check()
    assert found == ["tests/core/test_rates.py:2: a test of core/ (unit tier) may not import store/ (app.store.io): it "
                     "imports only what core/ may (parts.core.imports.may) [tiers]"]
    assert [(item["file"], item["line"], item["key"], item["why"]) for item in enforcement["accepted_findings"]] == [
        ("tests/core/test_rates.py", 1, "tiers.unit.accepted", "the rates read the table until the port lands"),
        ("tests/old/test_page.py", 0, "tiers.unit.accepted", "the old page tests are retired with the old page")]


def test_an_entry_that_accepts_nothing_is_a_tiers_finding():
    Path("tests/core/test_rates.py").write_text("from app.store import io\n")
    Path("tests/old/test_page.py").unlink()
    found, _ = check()
    assert [line for line in found if ":0: " in line] == [
        "tests/core/test_rates.py:0: tiers.unit.accepted accepts tests/core/test_rates.py importing store/db.py, and "
        "tiers finds none (tiers.unit.accepted) [tiers]",
        "tests/old/test_page.py:0: tiers.unit.accepted accepts the tiers findings of tests/old/test_page.py, and tiers "
        "finds none (tiers.unit.accepted) [tiers]"]


def test_an_entry_written_with_the_app_folder_first_is_told_to_write_its_path_below_the_app():
    profile("    accepted:\n      - {file: app/core/rates.py, why: the rates are old}\n")
    result = runner.invoke(app, ["check", "--profile", "tiered.yaml", "--format", "json"])
    assert [(v["file"], v["fix"]) for v in json.loads(result.stdout)["violations"]
                                       if "tiers.unit.accepted" in v["message"]] == [
        ("app/app/core/rates.py", "write the path relative to the app: core/rates.py, not app/core/rates.py")]


def test_with_no_entry_every_finding_is_reported():
    profile("")
    found, enforcement = check()
    assert len(found) == 3 and "accepted_findings" not in enforcement


def test_an_entry_with_no_reason_is_refused():
    profile("    accepted:\n      - {file: tests/old/test_page.py}\n")
    result = runner.invoke(app, ["profile", "check", "tiered.yaml"])
    assert result.exit_code != 0 and "tiers.unit.accepted.0: missing `why`" in result.stdout
