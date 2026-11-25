"""The pre-commit hook the repository ships, `.pre-commit-hooks.yaml`: it runs `xarch check` with the files staged as
its paths, in one run, so that their violations alone fail the commit; and the command it runs does that."""
from pathlib import Path

import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

HOOKS = Path(__file__).resolve().parents[2] / ".pre-commit-hooks.yaml"
runner = CliRunner()


def test_the_hook_runs_the_check_on_the_files_staged_in_one_run():
    hooks = yaml.safe_load(HOOKS.read_text(encoding="utf-8"))
    assert [(h["id"], h["entry"], h["pass_filenames"], h["require_serial"]) for h in hooks] == [
        ("xarch-check", "xarch check", True, True)]
    assert hooks[0]["language"] == "python"


def test_the_files_staged_fail_the_check_by_their_own_violations_alone(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0
    (tmp_path / "app/kernel/staged.py").write_text("A = 1\n")
    (tmp_path / "app/kernel/other.py").write_text("B = 1  # why\n")
    entry = yaml.safe_load(HOOKS.read_text(encoding="utf-8"))[0]["entry"].split()[1:]
    assert runner.invoke(app, [*entry, "app/kernel/staged.py", "README.md"]).exit_code == 0
    assert runner.invoke(app, [*entry, "app/kernel/staged.py", "app/kernel/other.py"]).exit_code == 1
