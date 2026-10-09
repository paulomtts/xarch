"""What every command shares: the --app and --profile options, choosing the profile, and how a refusal reaches the terminal."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import ProfileRefused, ProfileSelected, SelectProfile

AppPath = Annotated[Path, typer.Option("--app", help="The app/ folder to work on.")]
DEFAULT_APP = Path("app")
ProfileName = Annotated[str | None, typer.Option(
    "--profile", help="Skeleton profile: cli or web. Default: \\[tool.xarch] profile in pyproject.toml, else cli.")]


def fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(2)


def profile_for(spec: SpecController, app_path: Path, override: str | None) -> str:
    match spec.select(SelectProfile(app_path, override)):
        case ProfileSelected(name):
            return name
        case ProfileRefused(reason):
            raise fail(reason)
