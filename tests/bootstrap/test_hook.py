"""xarch hook claude: prints Claude Code's hooks for the project, the check of each file edited and the whole check
before the agent stops, and writes nothing; it needs no app and no profile."""
import json

from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.cli.reports.hook_report import claude_hooks

runner = CliRunner()


def test_the_hooks_are_printed_and_nothing_is_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["hook", "claude"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == json.loads(claude_hooks("xarch"))
    assert list(tmp_path.iterdir()) == []


def test_the_command_that_runs_xarch_may_be_given():
    result = runner.invoke(app, ["hook", "claude", "--command", "uv run xarch"])
    assert result.exit_code == 0 and json.loads(result.stdout) == json.loads(claude_hooks("uv run xarch"))


def test_an_agent_xarch_has_no_hooks_for_is_a_usage_error():
    result = runner.invoke(app, ["hook", "other"])
    assert result.exit_code == 2
