"""xarch check prints the state of its own enforcement after the violations, in text and in JSON, and --strict
fails on it; without --strict the section never changes the exit code."""
import json
import shutil
from pathlib import Path

import pytest
import typer
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
        "profile": {"location": "web", "bundled": True, "compared_with": None, "guards_off": [], "baseline_off": [],
                    "looser": []},
        "ungoverned": {"count": 0, "folders": [], "files": []},
        "excluded": [],
        "known": [],
        "translated": [],
        "init_files": [],
        "skipped": {"count": 0, "at": []},
        "dynamic": {"count": 0, "at": []},
        "unresolved": [],
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
        "  profile:     arch/open.yaml (custom; compared with web, closest; match 100%)",
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
    (tmp_path / "arch/mine.yaml").write_text(text.replace("  kernel/:\n", "  kernel/:\n    imports:\n      may: [platform]\n"))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:5] == [
        "  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)",
        "    guards off:  no-comments",
        "    imports.may: kernel may also import platform (parts.kernel.imports.may)"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-comments"]
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert "closest" not in profile
    compared = profile["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["match"], compared["low"]) == ("web", "closest", 1.0, False)
    assert compared["looser"] == profile["looser"]


def test_a_copy_of_a_bundled_profile_that_leaves_no_callbacks_out_shows_it_off_and_fails_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    assert "  no-callbacks: {parts: [domain, logic]}\n" in text
    (tmp_path / "arch/mine.yaml").write_text(text.replace("  no-callbacks: {parts: [domain, logic]}\n", ""))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:4] == [
        "  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)",
        "    guards off:  no-callbacks"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-callbacks"]
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert (profile["guards_off"], profile["baseline_off"]) == (["no-callbacks"], [])


def test_how_a_custom_profile_differs_from_the_closest_bundled_one_is_shown_and_never_fails_strict(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text()
    (tmp_path / "arch/mine.yaml").write_text(text.replace("  kernel/:\n", "  kernel/:\n    imports:\n      may: [platform]\n"))
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 0, strict.stdout
    assert "    imports.may: kernel may also import platform (parts.kernel.imports.may)" in strict.stdout.splitlines()
    assert "strict" not in strict.stdout
    document = json.loads(check("--profile", "arch/mine.yaml", "--strict", "--format", "json").stdout)
    assert document["ok"] is True and document["enforcement"]["strict_failures"] == []
    assert document["enforcement"]["profile"]["looser"] == [
        {"key": "imports.may", "part": "kernel", "what": "platform",
         "sentence": "kernel may also import platform (parts.kernel.imports.may)"}]


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
        "  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)",
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
        "  profile:     arch/mine.yaml (custom; compared with web, closest; match 100%)",
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


LOST = 'app/kernel/a.py:2: import ".ordr" names no file of the app'


def test_an_import_the_reader_could_not_follow_is_listed_and_fails_only_strict(tmp_path):
    (tmp_path / "app/kernel/a.py").write_text("x = 1\nfrom .ordr import X\n")
    result = check()
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines() == ["OK: no violations", "enforcement", "  profile:     web (bundled)",
                                          f"  unresolved:  {LOST}"]
    strict = check("--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", f"    unresolved: {LOST}"]
    document = json.loads(check("--format", "json").stdout)
    assert document["ok"] is True
    assert document["enforcement"]["unresolved"] == [{"file": "app/kernel/a.py", "line": 2, "written": ".ordr"}]
    assert document["enforcement"]["strict_failures"] == [{"key": "unresolved", "detail": LOST}]
    assert json.loads(check("--strict", "--format", "json").stdout)["ok"] is False


def test_the_help_of_strict_names_the_imports_the_reader_could_not_follow():
    command = typer.main.get_command(app).commands["check"]
    strict = next(param for param in command.params if "--strict" in param.opts)
    assert "dynamic imports, imports the reader could not follow, checks met to the letter" in strict.help


STRICT_AGAINST = ("--against shows a comparison and --strict fails on one: run `check --strict` without --against, "
                  "and it judges the profile against its baseline")


def test_against_compares_the_profile_in_force_for_the_run_and_leaves_the_exit_code_as_it_is(tmp_path):
    bundled = check("--against", "cli")
    assert bundled.exit_code == 0
    assert bundled.stdout.splitlines()[2] == "  profile:     web (bundled; compared with cli, --against; match 89%)"
    plant(tmp_path)
    custom = check("--profile", "arch/open.yaml", "--against", "cli")
    assert custom.exit_code == check("--profile", "arch/open.yaml").exit_code == 0
    assert custom.stdout.splitlines()[2] == (
        "  profile:     arch/open.yaml (custom; compared with cli, --against; match 89%)")


def test_against_changes_only_the_comparison_of_the_json_document(tmp_path):
    plant(tmp_path)
    plain = json.loads(check("--profile", "arch/open.yaml", "--format", "json").stdout)
    against = json.loads(check("--profile", "arch/open.yaml", "--against", "cli", "--format", "json").stdout)
    compared = against["enforcement"]["profile"]["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["higher"]) == ("cli", "against", None)
    assert plain["enforcement"]["strict_failures"]
    assert (against["ok"], against["violations"], against["enforcement"]["strict_failures"]) == (
        plain["ok"], plain["violations"], plain["enforcement"]["strict_failures"])


def test_strict_with_against_is_refused_before_anything_is_checked():
    text = check("--strict", "--against", "cli")
    assert text.exit_code == 2 and f"error: {STRICT_AGAINST}" in text.output
    missing = check("--app", "missing", "--strict", "--against", "cli")
    assert missing.exit_code == 2 and f"error: {STRICT_AGAINST}" in missing.output
    document = json.loads(check("--strict", "--against", "cli", "--format", "json").stdout)
    assert document == {"ok": False, "error": STRICT_AGAINST}


def test_check_against_a_profile_that_does_not_load_is_refused():
    result = check("--against", "nosuch")
    assert result.exit_code == 2
    assert ("error: --against does not load: nosuch: no bundled architecture 'nosuch': use one of cli, web, or a "
            "path to a .yaml or .json file") in result.output


@pytest.mark.parametrize("command", ["check", "profile check"])
def test_check_and_profile_check_take_against_the_profile_it_is_compared_with(command):
    found = typer.main.get_command(app)
    for name in command.split():
        found = found.commands[name]
    option = next(param for param in found.params if "--against" in param.opts)
    assert option.help == (
        "The profile it is compared with, for this run: the name of a bundled profile, or a path to a profile file "
        "(.yaml or .json) read from the working folder. Default: the one the profile's based_on names, else the "
        "bundled profile of highest match; a bundled profile is its own. Refused with --strict.")


def test_the_help_of_strict_names_the_profile_it_is_compared_with():
    command = typer.main.get_command(app).commands["check"]
    strict = next(param for param in command.params if "--strict" in param.opts)
    assert "guards left off that the profile it is compared with switches on (every guard, when none is compared)" in (
        strict.help)
    assert "compared bundled profile" not in strict.help


def chained(root: Path) -> None:
    """arch/team.yaml, a copy of web based on web that leaves no-comments off, and arch/mine.yaml, a copy of web based
    on team.yaml, read from its own folder, that leaves it off too, beside the bundled profiles' files."""
    shutil.copytree(BUNDLED, root / "arch")
    lax = (BUNDLED / "web.yaml").read_text().replace("  no-comments: {}\n", "")
    (root / "arch/team.yaml").write_text(lax.replace("\nname: web\n", "\nname: team\nbased_on: web\n", 1))
    (root / "arch/mine.yaml").write_text(lax.replace("\nname: web\n", "\nname: mine\nbased_on: team.yaml\n", 1))


def test_a_profile_based_on_a_file_of_its_own_says_what_strict_rests_on_and_the_file_excuses_no_guard(tmp_path):
    chained(tmp_path)
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 0, result.stdout
    assert result.stdout.splitlines()[2:4] == [
        "  profile:     arch/mine.yaml (custom; compared with team.yaml, based_on; match 100%; --strict rests on web)",
        "    guards off:  no-comments"]
    strict = check("--profile", "arch/mine.yaml", "--strict")
    assert strict.exit_code == 1
    assert strict.stdout.splitlines()[-2:] == ["strict:      1 finding fails the check", "    guards off: no-comments"]
    profile = json.loads(check("--profile", "arch/mine.yaml", "--format", "json").stdout)["enforcement"]["profile"]
    assert (profile["compared_with"]["anchor"], profile["guards_off"], profile["baseline_off"]) == (
        "web", ["no-comments"], [])


def test_check_refuses_a_profile_whose_based_on_file_does_not_load(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    (tmp_path / "arch/mine.yaml").write_text(
        (BUNDLED / "web.yaml").read_text().replace("\nname: web\n", "\nname: mine\nbased_on: gone.yaml\n", 1))
    result = check("--profile", "arch/mine.yaml")
    assert result.exit_code == 2
    assert "arch/mine.yaml: based_on: gone.yaml does not load: " in result.output
    assert "arch/gone.yaml: cannot read the file" in result.output
