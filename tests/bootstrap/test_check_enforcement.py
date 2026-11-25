"""xarch check prints the state of its own enforcement after the violations, in text and in JSON, and --strict
fails on it; without --strict the section never changes the exit code."""
import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xarch
from xarch.bootstrap.app import app

runner = CliRunner()
BUNDLED = Path(xarch.__file__).parent / "architectures"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "web"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "docs"]).exit_code == 0


def check(*arguments: str):
    return runner.invoke(app, ["check", *arguments])


def test_a_clean_bundled_project_shows_its_profile_and_the_guards_it_ships_off():
    result = check()
    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["OK: no violations", "enforcement", "  profile:     web (bundled)"]


def test_the_json_enforcement_always_holds_every_key():
    document = json.loads(check("--format", "json").stdout)
    assert document["strict"] is False
    assert document["enforcement"] == {
        "profile": {"location": "web", "bundled": True, "closest": None, "guards_off": [], "baseline_off": [],
                    "looser": []},
        "ungoverned": {"count": 0, "folders": [], "files": []},
        "excluded": [],
        "known": [],
        "translated": [],
        "init_files": [],
        "skipped": {"count": 0, "at": []},
        "dynamic": {"count": 0, "at": []},
        "weak": [],
        "approximate": [],
        "strict_failures": []}


def test_a_bundled_project_passes_strict_with_its_defaults():
    assert check("--strict").exit_code == 0


def plant(root: Path) -> None:
    """An ungoverned script, a dynamic import, a skipped test, and an edited guard test; and a copy of the bundled
    profile with closed-tree off, under which the script is no violation, only ungoverned."""
    shutil.copytree(BUNDLED, root / "arch")
    (root / "arch/open.yaml").write_text((BUNDLED / "web.yaml").read_text().replace("  closed-tree: {}\n", ""))
    (root / "app/scripts").mkdir()
    (root / "app/scripts/run.py").write_text("")
    (root / "app/kernel/dyn.py").write_text("import importlib\n\nplugin = importlib.import_module('app.x')\n")
    (root / "tests/modules/docs/domain").mkdir(parents=True)
    (root / "tests/modules/docs/domain/test_x.py").write_text("import pytest\n\n\n@pytest.mark.skip\ndef test_x():\n"
                                                              "    assert True\n")
    guard = root / "tests/architecture/test_rules.py"
    guard.write_text(guard.read_text() + "\n\ndef test_more():\n    assert True\n")


def test_every_finding_is_listed_after_the_summary_and_does_not_change_the_exit_code(tmp_path):
    plant(tmp_path)
    result = check("--profile", "arch/open.yaml")
    assert result.exit_code == 0
    assert result.stdout.splitlines() == [
        "OK: no violations", "enforcement",
        "  profile:     arch/open.yaml (custom; closest bundled: web)",
        "    guards off:  closed-tree",
        "  ungoverned:  1 Python file outside every part (app/scripts/)",
        "  init files:  tests/architecture/test_rules.py is changed",
        "  skipped:     1 skip (tests/modules/docs/domain/test_x.py:4)",
        "  dynamic:     1 dynamic import (app/kernel/dyn.py:3)"]


def test_strict_fails_on_every_finding_and_lists_them(tmp_path):
    plant(tmp_path)
    result = check("--profile", "arch/open.yaml", "--strict")
    assert result.exit_code == 1
    assert result.stdout.splitlines()[-6:] == [
        "strict:      5 findings fail the check",
        "    guards off: closed-tree",
        "    ungoverned: app/scripts/run.py",
        "    init files: tests/architecture/test_rules.py is changed",
        "    skipped: tests/modules/docs/domain/test_x.py:4",
        "    dynamic: app/kernel/dyn.py:3"]
    document = json.loads(check("--profile", "arch/open.yaml", "--strict", "--format", "json").stdout)
    assert (document["ok"], document["strict"], document["violations"]) == (False, True, [])
    assert document["enforcement"]["strict_failures"][1] == {"key": "ungoverned", "detail": "app/scripts/run.py"}
    assert document["enforcement"]["ungoverned"] == {"count": 1, "folders": ["app/scripts/"],
                                                     "files": ["app/scripts/run.py"]}


def test_a_custom_copy_of_a_bundled_profile_is_compared_with_it(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text().replace("  no-comments: {}\n", "")
    (tmp_path / "arch/mine.yaml").write_text(text.replace("    path: kernel\n", "    path: kernel\n    may_import: [platform]\n"))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:5] == [
        "  profile:     arch/mine.yaml (custom; closest bundled: web)",
        "    guards off:  no-comments",
        "    may_import:  kernel may also import platform (parts.kernel.may_import)"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-comments"]


def test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_shown_and_never_fails_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    (tmp_path / "arch/mine.yaml").write_text(text.replace("    path: kernel\n", "    path: kernel\n    may_import: [platform]\n"))
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 0, strict.stdout
    assert "    may_import:  kernel may also import platform (parts.kernel.may_import)" in strict.stdout.splitlines()
    assert "strict" not in strict.stdout
    document = json.loads(check("--profile", "arch/mine.yaml", "--strict", "--format", "json").stdout)
    assert document["ok"] is True and document["enforcement"]["strict_failures"] == []
    assert document["enforcement"]["profile"]["looser"] == [
        {"key": "may_import", "part": "kernel", "what": "platform",
         "sentence": "kernel may also import platform (parts.kernel.may_import)"}]


def test_a_custom_profile_whose_tier_no_longer_applies_the_never_lists_is_looser_under_uses_apply_never(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    assert text.count("    uses: {apply_never: true}\n") == 1
    (tmp_path / "arch/mine.yaml").write_text(text.replace("    uses: {apply_never: true}\n", ""))
    document = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)
    assert document["enforcement"]["profile"]["looser"] == [
        {"key": "uses.apply_never", "part": "unit", "what": "",
         "sentence": "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"}]


def test_an_excluded_folder_is_never_read_is_listed_and_does_not_fail_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text() + "\nexcluded:\n  scripts: example scripts the docs show\n"
    (tmp_path / "arch/mine.yaml").write_text(text)
    (tmp_path / "app/scripts").mkdir()
    (tmp_path / "app/scripts/run.py").write_text("def (:\n")
    result = check("--profile", "arch/mine.yaml", "--strict")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines() == [
        "OK: no violations", "enforcement",
        "  profile:     arch/mine.yaml (custom; closest bundled: web)",
        "  excluded:    app/scripts/ (example scripts the docs show)"]
    document = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)
    assert document["enforcement"]["excluded"] == [{"folder": "app/scripts", "reason": "example scripts the docs show"}]
    assert document["enforcement"]["ungoverned"]["count"] == 0


def test_a_public_name_the_profile_accepts_as_only_the_tests_is_named_and_an_entry_that_no_longer_holds_fails_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text().replace(
        "  dead-code: {untested: true}\n",
        "  dead-code: {untested: true, tests_only: true, known: [kernel/ids.py:make, kernel/ids.py:gone]}\n")
    (tmp_path / "arch/mine.yaml").write_text(text)
    (tmp_path / "app/kernel/ids.py").write_text("def make():\n    return 1\n")
    (tmp_path / "tests/kernel").mkdir(exist_ok=True)
    (tmp_path / "tests/kernel/test_ids.py").write_text("from app.kernel.ids import make\n\n\ndef test_make():\n"
                                                       "    assert make() == 1\n")
    gone = ("app/kernel/ids.py: kernel/ids.py defines no public class or top-level function gone, which "
            "guards.dead-code.known lists (guards.dead-code.known)")
    result = check("--profile", "arch/mine.yaml", "--strict")
    assert result.exit_code == 1
    assert result.stdout.splitlines() == [
        "OK: no violations", "enforcement",
        "  profile:     arch/mine.yaml (custom; closest bundled: web)",
        "    known:       the tests-only check accepts kernel/ids.py:make as a name only the tests use "
        "(guards.dead-code.known)",
        "    known:       the tests-only check accepts kernel/ids.py:gone as a name only the tests use "
        "(guards.dead-code.known)",
        "  known:       app/kernel/ids.py:1: make is public, a test names it and no other file of the app does, "
        "which the profile accepts (guards.dead-code.known)",
        f"  weak:        {gone}",
        "      fix: drop kernel/ids.py:gone from guards.dead-code.known, or name the file and the name as they are now",
        "strict:      1 finding fails the check",
        f"    weak: {gone}"]
    document = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)
    assert document["enforcement"]["known"] == [{"file": "app/kernel/ids.py", "line": 1, "name": "make"}]
