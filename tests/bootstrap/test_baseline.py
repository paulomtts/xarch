"""The baseline through the real app: `xarch baseline write` records the violations a whole check finds now in
.xarch/baseline.json, `check` then holds them back and reports only what the record does not hold, says how far the
record is above the code and fails `--strict` until it is lowered; a write only lowers an existing record, unless
--reset; with no record, check is as it was."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: ringed
parts:
  web/:
    role: the web ring
  core/:
    role: the rules
"""
RECORD = Path(".xarch/baseline.json")


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("ringed.yaml").write_text(PROFILE)
    for path, text in {"app/__init__.py": "", "app/web/__init__.py": "", "app/web/page.py": "P = 1\n",
                       "app/web/form.py": "F = 1\n", "app/core/__init__.py": "",
                       "app/core/rules.py": "from app.web import page\n"}.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)


def run(*args: str):
    return runner.invoke(app, [*args, "--profile", "ringed.yaml"])


def check(*args: str) -> tuple[int, dict]:
    result = run("check", "--format", "json", *args)
    return result.exit_code, json.loads(result.stdout)


def test_with_no_record_check_reports_every_violation_and_says_nothing_of_a_baseline():
    code, document = check()
    assert code == 1 and len(document["violations"]) == 1 and "baseline" not in document["enforcement"]


def test_a_violation_the_record_holds_is_held_back_and_counted():
    written = run("baseline", "write")
    assert written.exit_code == 0, written.stdout
    assert "baseline: .xarch/baseline.json records 1 violation(s) (no record before)" in written.stdout
    assert json.loads(RECORD.read_text())["findings"][0]["rule"] == "may-import"
    code, document = check()
    assert (code, document["violations"]) == (0, [])
    assert document["enforcement"]["baseline"] == {
        "file": ".xarch/baseline.json", "recorded": 1, "baselined": 1, "below": 0,
        "rules": [{"rule": "may-import", "recorded": 1, "found": 1}]}


def test_a_new_violation_is_reported_though_one_of_its_rule_is_held_back():
    run("baseline", "write")
    Path("app/core/rules.py").write_text("from app.web import page\nfrom app.web import form\n")
    code, document = check()
    assert code == 1 and [v["message"] for v in document["violations"]] == [
        "core/ may not import web/ (app.web.form)"]


def test_a_line_moving_keeps_a_violation_held_back():
    run("baseline", "write")
    Path("app/core/rules.py").write_text("\n\nfrom app.web import page\n")
    assert check()[0] == 0


def test_a_swap_is_caught_one_fixed_and_another_added():
    run("baseline", "write")
    Path("app/core/rules.py").write_text("from app.web import form\n")
    code, document = check()
    assert code == 1 and document["enforcement"]["baseline"]["below"] == 1


def test_a_record_above_the_code_passes_says_so_and_fails_strict_until_it_is_lowered():
    run("baseline", "write")
    Path("app/core/rules.py").write_text("")
    code, document = check()
    assert code == 0 and document["enforcement"]["baseline"]["below"] == 1
    text = run("check").stdout
    assert "1 below baseline: run `xarch baseline write` to lower it" in text
    strict = run("check", "--strict", "--format", "json")
    assert strict.exit_code == 1
    assert {"key": "baseline", "detail": "1 finding(s) below baseline (.xarch/baseline.json): run `xarch baseline "
                                         "write` to lower it"} in json.loads(strict.stdout)["enforcement"]["strict_failures"]
    run("baseline", "write")
    assert json.loads(RECORD.read_text())["findings"] == []
    assert json.loads(run("check", "--format", "json").stdout)["enforcement"]["baseline"]["below"] == 0


def test_a_write_only_lowers_an_existing_record_unless_reset():
    run("baseline", "write")
    Path("app/core/rules.py").write_text("from app.web import page\nfrom app.web import form\n")
    run("baseline", "write")
    assert len(json.loads(RECORD.read_text())["findings"]) == 1
    assert check()[0] == 1
    reset = run("baseline", "write", "--reset")
    assert "records 2 violation(s) (1 before, written afresh)" in reset.stdout
    assert check()[0] == 0


def test_a_partial_check_applies_the_record_to_the_whole_app_first():
    run("baseline", "write")
    code, document = check("app/core/rules.py")
    assert (code, document["violations"], document["partial"]["elsewhere"]) == (0, [], 0)


def test_a_record_that_cannot_be_read_is_refused():
    RECORD.parent.mkdir()
    RECORD.write_text("{")
    result = run("check")
    assert result.exit_code == 2 and "the baseline" in result.stdout + (result.stderr or "")


def rules_recorded() -> list[tuple[str, int]]:
    return [(item["rule"], item["count"]) for item in json.loads(RECORD.read_text())["findings"]]


def test_a_write_of_one_rule_records_that_rule_alone():
    Path("app/core/bad.py").write_text("def (\n")
    written = run("baseline", "write", "--rule", "may-import", "--format", "json")
    assert written.exit_code == 0, written.stdout
    assert json.loads(written.stdout)["rule"] == "may-import"
    assert rules_recorded() == [("may-import", 1)]
    code, document = check()
    assert (code, [v["rule"] for v in document["violations"]]) == (1, ["syntax"])


def test_a_write_of_one_rule_lowers_or_resets_that_rule_and_keeps_the_others_as_they_are():
    Path("app/core/bad.py").write_text("def (\n")
    run("baseline", "write")
    assert rules_recorded() == [("may-import", 1), ("syntax", 1)]
    Path("app/core/bad.py").unlink()
    Path("app/core/rules.py").write_text("")
    lowered = run("baseline", "write", "--rule", "syntax")
    assert "(2 before; only syntax written, every other rule kept)" in lowered.stdout
    assert rules_recorded() == [("may-import", 1)]
    Path("app/core/rules.py").write_text("from app.web import page\nfrom app.web import form\n")
    assert run("baseline", "write", "--rule", "may-import").exit_code == 0
    assert rules_recorded() == [("may-import", 1)]
    assert run("baseline", "write", "--rule", "may-import", "--reset").exit_code == 0
    assert sorted(rules_recorded()) == [("may-import", 1), ("may-import", 1)]


def test_a_write_of_a_rule_check_does_not_have_is_refused():
    written = run("baseline", "write", "--rule", "may-imports")
    assert written.exit_code == 2
    assert "may-imports is no rule of check" in written.output
