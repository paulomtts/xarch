"""xarch hook: prints the hooks a coding agent runs the check with, for the project to add to the agent's settings;
writes nothing, and reads no app and no profile."""
from enum import Enum
from typing import Annotated

import typer

from xarch.cli.reports.hook_report import claude_hooks
from xarch.cli.terminal import echo, rewrapped


class Agent(str, Enum):
    claude = "claude"


AgentArgument = Annotated[Agent, typer.Argument(help="The agent whose hooks to print: `claude`, for Claude Code.")]
CommandOption = Annotated[str, typer.Option(
    "--command", help="How the hooks run xarch, such as `uv run xarch` when it is a dev dependency of the project and "
                      "not on the PATH.")]


def register(app: typer.Typer) -> None:
    @app.command()
    @rewrapped
    def hook(agent: AgentArgument, command: CommandOption = "xarch") -> None:
        """Print the hooks that run the check for a coding agent, as its settings hold them; nothing is written.

        For Claude Code: after each edit or write, the check of the file written (`xarch check --files-from -`);
        before the agent stops, `xarch check --strict`, the guard test's; each hands the check's output back to the
        agent when it fails. Add the `hooks` key to `.claude/settings.json` (or `.claude/settings.local.json`); they
        need jq."""
        echo([claude_hooks(command)])
